#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Cluster Profiler Service
=============================
Service để generate mô tả chi tiết về student clusters sử dụng LLM
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)


class LLMClusterProfiler:
    """
    Service sử dụng LLM để phân tích và mô tả student clusters
    
    Features:
    - Generate natural language descriptions cho clusters
    - Phân tích strengths/weaknesses
    - Đưa ra recommendations cụ thể
    - Support Gemini và OpenAI
    """
    
    def __init__(self, 
                 cluster_profiles_path: str,
                 llm_provider: str = 'gemini',
                 api_key: Optional[str] = None):
        """
        Initialize LLM Cluster Profiler
        
        Args:
            cluster_profiles_path: Path to cluster_profiles.json
            llm_provider: 'gemini' or 'openai'
            api_key: API key (if None, read from env)
        """
        self.cluster_profiles_path = Path(cluster_profiles_path)
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key
        self.llm_client = None
        self.cluster_profiles = None
        
        # Load cluster profiles
        self._load_cluster_profiles()
        
        # Initialize LLM
        self._initialize_llm()
    
    def _load_cluster_profiles(self):
        """Load cluster profiles from JSON"""
        if not self.cluster_profiles_path.exists():
            raise FileNotFoundError(f"Cluster profiles not found: {self.cluster_profiles_path}")
        
        with open(self.cluster_profiles_path, 'r', encoding='utf-8') as f:
            self.cluster_profiles = json.load(f)
        
        logger.info(f"✓ Loaded cluster profiles: {len(self.cluster_profiles.get('cluster_stats', {}))} clusters")
    
    def _initialize_llm(self):
        """Initialize LLM client"""
        try:
            if self.llm_provider == 'gemini':
                import google.generativeai as genai
                
                # Try: 1) provided api_key, 2) env vars, 3) config file
                api_key = self.api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                
                # If still not found, try to load from config
                if not api_key:
                    try:
                        import sys
                        from pathlib import Path
                        config_path = Path(__file__).parent.parent / 'config.py'
                        if config_path.exists():
                            import importlib.util
                            spec = importlib.util.spec_from_file_location("config", config_path)
                            config = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(config)
                            api_key = getattr(config, 'GEMINI_API_KEY', '') or getattr(config, 'GOOGLE_API_KEY', '')
                    except Exception:
                        pass
                
                if not api_key:
                    raise ValueError("Gemini API key not found. Set GOOGLE_API_KEY/GEMINI_API_KEY env var or add to config.py")
                
                genai.configure(api_key=api_key)
                self.llm_client = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✓ Initialized Gemini LLM")
                
            elif self.llm_provider == 'openai':
                from openai import OpenAI
                
                # Try: 1) provided api_key, 2) env var, 3) config file
                api_key = self.api_key or os.getenv('OPENAI_API_KEY')
                
                # If still not found, try to load from config
                if not api_key:
                    try:
                        import sys
                        from pathlib import Path
                        config_path = Path(__file__).parent.parent / 'config.py'
                        if config_path.exists():
                            import importlib.util
                            spec = importlib.util.spec_from_file_location("config", config_path)
                            config = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(config)
                            api_key = getattr(config, 'OPENAI_API_KEY', '')
                    except Exception:
                        pass
                
                if not api_key:
                    raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY env var or add to config.py")
                
                self.llm_client = OpenAI(api_key=api_key)
                logger.info("✓ Initialized OpenAI LLM")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            logger.warning("⚠ LLM not available. Will use fallback descriptions.")
            self.llm_client = None
    
    def _format_top_features(self, cluster_data: Dict) -> str:
        """Format top distinguishing features cho prompt"""
        top_features = cluster_data.get('top_distinguishing_features', [])[:5]
        
        lines = []
        for feat_data in top_features:
            feat = feat_data.get('feature', 'unknown')
            interp = feat_data.get('interpretation', 'similar')
            z = feat_data.get('z_score', 0.0)
            lines.append(f"  - {feat}: {interp} (z-score: {z:.2f})")
        
        return '\n'.join(lines) if lines else "  - No distinguishing features"
    
    def generate_cluster_description(self, cluster_id: int) -> Dict:
        """
        Generate LLM description cho 1 cluster
        
        Args:
            cluster_id: Cluster ID
            
        Returns:
            Dict with name, description, strengths, weaknesses, recommendations
        """
        if not self.cluster_profiles:
            raise ValueError("Cluster profiles not loaded")
        
        cluster_stats = self.cluster_profiles.get('cluster_stats', {})
        cluster_key = str(cluster_id)
        
        if cluster_key not in cluster_stats:
            raise ValueError(f"Cluster {cluster_id} not found")
        
        cluster_data = cluster_stats[cluster_key]
        
        # If LLM not available, return fallback
        if not self.llm_client:
            return self._generate_fallback_description(cluster_data)
        
        # Prepare LLM prompt
        prompt = f"""
Bạn là một chuyên gia phân tích dữ liệu giáo dục trên hệ thống Moodle. Hãy phân tích và mô tả đặc điểm của nhóm học sinh sau:

**Thông tin nhóm:**
- Cluster ID: {cluster_id}
- Số lượng: {cluster_data.get('n_students', 0)} học sinh ({cluster_data.get('percentage', 0):.1f}% tổng số)
- Top 5 đặc điểm nổi bật so với overall:
{self._format_top_features(cluster_data)}

**Yêu cầu:**
1. Đặt tên ngắn gọn cho nhóm này (tối đa 5 từ, ví dụ: "Học sinh Xuất sắc Toàn diện", "Học sinh Cần Hỗ trợ Cơ bản", v.v.)
2. Mô tả đặc điểm học tập của nhóm (2-3 câu, tập trung vào hành vi học tập trên Moodle)
3. Phân tích 2-3 điểm mạnh chính
4. Phân tích 2-3 điểm yếu/thách thức chính
5. Đề xuất 3 hành động cụ thể để hỗ trợ hoặc phát triển nhóm này

**Lưu ý:**
- Phân tích dựa trên các features Moodle (course_viewed, submission, assessment, etc.)
- Đưa ra insights thực tế, dễ hiểu
- Recommendations phải cụ thể, có thể thực hiện được

**Định dạng trả về (chỉ JSON, không có markdown backticks):**
{{
    "profile_name": "Tên nhóm ngắn gọn",
    "description": "Mô tả ngắn gọn về đặc điểm học tập",
    "strengths": ["Điểm mạnh 1", "Điểm mạnh 2", "Điểm mạnh 3"],
    "weaknesses": ["Điểm yếu 1", "Điểm yếu 2"],
    "recommendations": ["Hành động 1", "Hành động 2", "Hành động 3"],
    "key_characteristics": ["Đặc điểm 1", "Đặc điểm 2"]
}}
"""
        
        try:
            # Call LLM
            if self.llm_provider == 'gemini':
                response = self.llm_client.generate_content(prompt)
                result_text = response.text
            else:  # openai
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an educational data analyst. Always respond in Vietnamese and return valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                result_text = response.choices[0].message.content
            
            # Clean and parse JSON
            result_text = result_text.strip()
            
            # Remove markdown code blocks
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            elif result_text.startswith('```'):
                result_text = result_text[3:]
            
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            
            # Parse JSON
            result = json.loads(result_text)
            
            # Validate required fields
            required_fields = ['profile_name', 'description', 'strengths', 'weaknesses', 'recommendations']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field '{field}' in LLM response for cluster {cluster_id}")
                    result[field] = [] if field in ['strengths', 'weaknesses', 'recommendations'] else "N/A"
            
            logger.info(f"✓ Generated LLM description for Cluster {cluster_id}: {result.get('profile_name', 'N/A')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response for cluster {cluster_id}: {e}")
            logger.error(f"Response text: {result_text[:200]}...")
            return self._generate_fallback_description(cluster_data)
            
        except Exception as e:
            logger.error(f"LLM generation failed for cluster {cluster_id}: {e}")
            return self._generate_fallback_description(cluster_data)
    
    def _generate_fallback_description(self, cluster_data: Dict) -> Dict:
        """Generate basic description when LLM not available"""
        cluster_id = cluster_data.get('cluster_id', 0)
        n_students = cluster_data.get('n_students', 0)
        pct = cluster_data.get('percentage', 0)
        
        # Simple rule-based naming
        if pct > 40:
            name = f"Nhóm Đa số ({pct:.0f}%)"
        elif pct < 10:
            name = f"Nhóm Thiểu số ({pct:.0f}%)"
        else:
            name = f"Nhóm {cluster_id}"
        
        return {
            'profile_name': name,
            'description': f"Nhóm gồm {n_students} học sinh, chiếm {pct:.1f}% tổng số. Cần phân tích chi tiết với LLM để có insights đầy đủ.",
            'strengths': ["Cần phân tích với LLM để xác định"],
            'weaknesses': ["Cần phân tích với LLM để xác định"],
            'recommendations': ["Kích hoạt LLM (Gemini/OpenAI) để có recommendations cụ thể"],
            'key_characteristics': ["Cần LLM để phân tích"]
        }
    
    def generate_all_clusters(self) -> Dict:
        """
        Generate descriptions cho tất cả clusters
        
        Returns:
            Dict with all cluster profiles
        """
        if not self.cluster_profiles:
            raise ValueError("Cluster profiles not loaded")
        
        cluster_stats = self.cluster_profiles.get('cluster_stats', {})
        results = {}
        
        logger.info(f"Generating LLM descriptions for {len(cluster_stats)} clusters...")
        
        for cluster_key in sorted(cluster_stats.keys(), key=lambda x: int(x)):
            cluster_id = int(cluster_key)
            logger.info(f"\n📊 Analyzing Cluster {cluster_id}...")
            
            description = self.generate_cluster_description(cluster_id)
            
            # Add to results
            results[cluster_key] = {
                'cluster_id': cluster_id,
                'statistics': cluster_stats[cluster_key],
                'ai_profile': description
            }
        
        logger.info(f"\n✓ Generated descriptions for {len(results)} clusters")
        return results
    
    def save_profiles(self, output_path: str):
        """
        Save cluster profiles with LLM descriptions
        
        Args:
            output_path: Output file path (JSON)
        """
        profiles = self.generate_all_clusters()
        
        output = {
            'metadata': {
                'llm_provider': self.llm_provider,
                'n_clusters': len(profiles),
                'total_students': self.cluster_profiles.get('total_students', 0)
            },
            'clusters': profiles
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved LLM profiles to: {output_file}")
        
        # Also save human-readable report
        self._save_text_report(profiles, output_file.parent / 'cluster_profiles_llm_report.txt')
    
    def _save_text_report(self, profiles: Dict, output_path: Path):
        """Save human-readable text report"""
        lines = []
        lines.append("="*80)
        lines.append("CLUSTER PROFILING REPORT (LLM-POWERED)")
        lines.append("="*80)
        lines.append(f"\nLLM Provider: {self.llm_provider.upper()}")
        lines.append(f"Total Clusters: {len(profiles)}")
        lines.append(f"Total Students: {self.cluster_profiles.get('total_students', 0)}")
        
        for cluster_key in sorted(profiles.keys(), key=lambda x: int(x)):
            data = profiles[cluster_key]
            stats = data['statistics']
            ai = data['ai_profile']
            
            lines.append("\n" + "="*80)
            lines.append(f"CLUSTER {data['cluster_id']}: {ai.get('profile_name', 'N/A')}")
            lines.append("="*80)
            
            lines.append(f"\n📊 Thống kê:")
            lines.append(f"  • Số lượng: {stats.get('n_students', 0)} học sinh ({stats.get('percentage', 0):.1f}%)")
            
            lines.append(f"\n📝 Mô tả:")
            lines.append(f"  {ai.get('description', 'N/A')}")
            
            lines.append(f"\n🎯 Đặc điểm chính:")
            for char in ai.get('key_characteristics', []):
                lines.append(f"  • {char}")
            
            lines.append(f"\n💪 Điểm mạnh:")
            for strength in ai.get('strengths', []):
                lines.append(f"  • {strength}")
            
            lines.append(f"\n⚠️ Điểm yếu:")
            for weakness in ai.get('weaknesses', []):
                lines.append(f"  • {weakness}")
            
            lines.append(f"\n💡 Đề xuất hành động:")
            for i, rec in enumerate(ai.get('recommendations', []), 1):
                lines.append(f"  {i}. {rec}")
        
        lines.append("\n" + "="*80)
        lines.append("END OF REPORT")
        lines.append("="*80)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"✓ Saved text report to: {output_path}")
