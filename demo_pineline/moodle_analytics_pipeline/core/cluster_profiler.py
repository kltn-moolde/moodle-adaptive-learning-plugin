#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster Profiler Module (LLM-powered)
======================================
Sử dụng LLM để phân tích và mô tả đặc điểm của từng cluster
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ClusterProfiler:
    """
    Phân tích và mô tả đặc điểm của từng cluster sử dụng LLM
    
    Features:
    - Tính toán statistical profile cho mỗi cluster
    - Sử dụng LLM (Gemini/OpenAI) để generate mô tả tự nhiên
    - So sánh cluster với overall population
    - Tạo actionable insights và recommendations
    """
    
    def __init__(self, llm_provider: str = 'gemini', api_key: Optional[str] = None):
        """
        Args:
            llm_provider: 'gemini' hoặc 'openai'
            api_key: API key (nếu None, sẽ đọc từ env variable)
        """
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key
        self.llm_client = None
        self.cluster_profiles = {}
        
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client"""
        try:
            if self.llm_provider == 'gemini':
                import google.generativeai as genai
                import os
                
                api_key = self.api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                if not api_key:
                    raise ValueError("Gemini API key not found. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
                
                genai.configure(api_key=api_key)
                # Sử dụng gemini-2.5-flash (model mới, thay thế gemini-1.5-flash)
                self.llm_client = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✓ Initialized Gemini LLM (gemini-2.5-flash)")
                
            elif self.llm_provider == 'openai':
                from openai import OpenAI
                import os
                
                api_key = self.api_key or os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
                
                self.llm_client = OpenAI(api_key=api_key)
                logger.info("✓ Initialized OpenAI LLM")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}. Use 'gemini' or 'openai'")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            logger.warning("⚠ LLM not available. Will generate basic profiles without AI descriptions.")
            self.llm_client = None
    
    def calculate_cluster_statistics(self, df: pd.DataFrame, cluster_col: str = 'cluster') -> Dict:
        """
        Tính toán statistics cho từng cluster
        
        Args:
            df: DataFrame chứa data với cluster labels
            cluster_col: Tên column chứa cluster ID
            
        Returns:
            Dict với cluster statistics
        """
        logger.info("Calculating cluster statistics...")
        
        # Get feature columns (exclude metadata)
        exclude_cols = ['userid', 'cluster', 'group']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Overall statistics
        overall_stats = {
            'mean': df[feature_cols].mean().to_dict(),
            'std': df[feature_cols].std().to_dict(),
            'median': df[feature_cols].median().to_dict()
        }
        
        # Per-cluster statistics
        cluster_stats = {}
        
        for cluster_id in sorted(df[cluster_col].unique()):
            cluster_df = df[df[cluster_col] == cluster_id]
            n_students = len(cluster_df)
            pct_students = (n_students / len(df)) * 100
            
            # Feature statistics
            cluster_mean = cluster_df[feature_cols].mean()
            cluster_std = cluster_df[feature_cols].std()
            cluster_median = cluster_df[feature_cols].median()
            
            # Compare to overall (z-score like)
            deviation_from_overall = {}
            for feat in feature_cols:
                if overall_stats['std'][feat] > 0:
                    z_score = (cluster_mean[feat] - overall_stats['mean'][feat]) / overall_stats['std'][feat]
                    deviation_from_overall[feat] = float(z_score)
                else:
                    deviation_from_overall[feat] = 0.0
            
            # Identify top distinguishing features (highest absolute deviation)
            top_features = sorted(deviation_from_overall.items(), 
                                 key=lambda x: abs(x[1]), 
                                 reverse=True)[:5]
            
            cluster_stats[int(cluster_id)] = {
                'cluster_id': int(cluster_id),
                'n_students': int(n_students),
                'percentage': float(pct_students),
                'feature_means': {k: float(v) for k, v in cluster_mean.items()},
                'feature_stds': {k: float(v) for k, v in cluster_std.items()},
                'feature_medians': {k: float(v) for k, v in cluster_median.items()},
                'deviation_from_overall': deviation_from_overall,
                'top_distinguishing_features': [
                    {
                        'feature': feat,
                        'z_score': float(z_score),
                        'interpretation': 'much higher' if z_score > 1.5 else 
                                        'higher' if z_score > 0.5 else
                                        'much lower' if z_score < -1.5 else
                                        'lower' if z_score < -0.5 else
                                        'similar'
                    }
                    for feat, z_score in top_features
                ]
            }
        
        self.cluster_profiles = {
            'overall_stats': overall_stats,
            'cluster_stats': cluster_stats,
            'n_clusters': len(cluster_stats),
            'total_students': len(df),
            'features_analyzed': feature_cols
        }
        
        logger.info(f"✓ Calculated statistics for {len(cluster_stats)} clusters")
        return self.cluster_profiles
    
    def generate_llm_description(self, cluster_id: int) -> str:
        """
        Sử dụng LLM để generate mô tả tự nhiên cho cluster
        
        Args:
            cluster_id: ID của cluster cần mô tả
            
        Returns:
            Mô tả bằng tiếng Việt
        """
        if not self.llm_client:
            return "LLM not available. Using basic description."
        
        cluster_data = self.cluster_profiles['cluster_stats'][cluster_id]
        
        # Prepare prompt
        prompt = f"""
Bạn là một chuyên gia phân tích dữ liệu giáo dục. Hãy phân tích và mô tả đặc điểm của nhóm học sinh sau:

**Thông tin nhóm:**
- Số lượng: {cluster_data['n_students']} học sinh ({cluster_data['percentage']:.1f}% tổng số)
- Top 5 đặc điểm nổi bật:
{self._format_top_features(cluster_data['top_distinguishing_features'])}

**Yêu cầu:**
1. Đặt tên cho nhóm này (ví dụ: "Học sinh xuất sắc", "Học sinh cần hỗ trợ", v.v.)
2. Mô tả đặc điểm học tập của nhóm (2-3 câu)
3. Phân tích điểm mạnh và điểm yếu
4. Đề xuất 2-3 hành động cụ thể để hỗ trợ/phát triển nhóm này

**Định dạng trả về (JSON):**
{{
    "name": "Tên nhóm",
    "description": "Mô tả ngắn gọn",
    "strengths": ["Điểm mạnh 1", "Điểm mạnh 2"],
    "weaknesses": ["Điểm yếu 1", "Điểm yếu 2"],
    "recommendations": ["Hành động 1", "Hành động 2", "Hành động 3"]
}}

Chỉ trả về JSON, không thêm text khác.
"""
        
        try:
            if self.llm_provider == 'gemini':
                response = self.llm_client.generate_content(prompt)
                result_text = response.text
            else:  # openai
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an educational data analyst. Always respond in Vietnamese and return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                result_text = response.choices[0].message.content
            
            # Parse JSON from response
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            logger.error(f"LLM generation failed for cluster {cluster_id}: {e}")
            return self._generate_fallback_description(cluster_id)
    
    def _format_top_features(self, top_features: List[Dict]) -> str:
        """Format top features cho prompt"""
        lines = []
        for feat_data in top_features:
            feat = feat_data['feature']
            interp = feat_data['interpretation']
            z = feat_data['z_score']
            lines.append(f"  - {feat}: {interp} (z-score: {z:.2f})")
        return '\n'.join(lines)
    
    def _generate_fallback_description(self, cluster_id: int) -> Dict:
        """Generate basic description khi LLM không available"""
        cluster_data = self.cluster_profiles['cluster_stats'][cluster_id]
        
        # Simple rule-based naming
        pct = cluster_data['percentage']
        if pct > 40:
            name = "Nhóm đa số"
        elif pct < 10:
            name = "Nhóm thiểu số"
        else:
            name = f"Nhóm {cluster_id + 1}"
        
        return {
            'name': name,
            'description': f"Nhóm gồm {cluster_data['n_students']} học sinh ({pct:.1f}%).",
            'strengths': ["Cần phân tích thêm"],
            'weaknesses': ["Cần phân tích thêm"],
            'recommendations': ["Cần phân tích chi tiết hơn để đưa ra đề xuất phù hợp"]
        }
    
    def profile_all_clusters(self, df: pd.DataFrame, cluster_col: str = 'cluster') -> Dict:
        """
        Phân tích và mô tả tất cả các cluster
        
        Args:
            df: DataFrame chứa data với cluster labels
            cluster_col: Tên column chứa cluster ID
            
        Returns:
            Dict với cluster profiles
        """
        logger.info("="*70)
        logger.info("CLUSTER PROFILING WITH LLM")
        logger.info("="*70)
        
        # Calculate statistics
        self.calculate_cluster_statistics(df, cluster_col)
        
        # Generate LLM descriptions
        logger.info("\nGenerating AI-powered descriptions for each cluster...")
        
        for cluster_id in sorted(self.cluster_profiles['cluster_stats'].keys()):
            logger.info(f"\n📊 Analyzing Cluster {cluster_id}...")
            
            llm_description = self.generate_llm_description(cluster_id)
            self.cluster_profiles['cluster_stats'][cluster_id]['ai_profile'] = llm_description
            
            logger.info(f"  ✓ Name: {llm_description.get('name', 'N/A')}")
            logger.info(f"  ✓ Description: {llm_description.get('description', 'N/A')}")
        
        logger.info("\n" + "="*70)
        logger.info(f"✓ Profiled {len(self.cluster_profiles['cluster_stats'])} clusters")
        logger.info("="*70)
        
        return self.cluster_profiles
    
    def save_profiles(self, output_dir: str):
        """
        Lưu cluster profiles
        
        Args:
            output_dir: Directory to save profiles
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = output_path / 'cluster_profiles.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.cluster_profiles, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ Saved: {json_path}")
        
        # Save human-readable report
        self._save_text_report(output_path)
    
    def _save_text_report(self, output_path: Path):
        """Lưu báo cáo text dễ đọc"""
        text_lines = []
        text_lines.append("="*80)
        text_lines.append("CLUSTER PROFILING REPORT (AI-POWERED)")
        text_lines.append("="*80)
        text_lines.append(f"\nTổng số học sinh: {self.cluster_profiles['total_students']}")
        text_lines.append(f"Số cụm: {self.cluster_profiles['n_clusters']}")
        text_lines.append(f"Số features phân tích: {len(self.cluster_profiles['features_analyzed'])}")
        
        for cluster_id in sorted(self.cluster_profiles['cluster_stats'].keys()):
            data = self.cluster_profiles['cluster_stats'][cluster_id]
            ai_profile = data.get('ai_profile', {})
            
            text_lines.append("\n" + "="*80)
            text_lines.append(f"CLUSTER {cluster_id}: {ai_profile.get('name', 'N/A')}")
            text_lines.append("="*80)
            text_lines.append(f"\n📊 Thống kê:")
            text_lines.append(f"  • Số lượng: {data['n_students']} học sinh ({data['percentage']:.1f}%)")
            
            text_lines.append(f"\n📝 Mô tả:")
            text_lines.append(f"  {ai_profile.get('description', 'N/A')}")
            
            text_lines.append(f"\n💪 Điểm mạnh:")
            for strength in ai_profile.get('strengths', []):
                text_lines.append(f"  • {strength}")
            
            text_lines.append(f"\n⚠️ Điểm yếu:")
            for weakness in ai_profile.get('weaknesses', []):
                text_lines.append(f"  • {weakness}")
            
            text_lines.append(f"\n💡 Đề xuất hành động:")
            for i, rec in enumerate(ai_profile.get('recommendations', []), 1):
                text_lines.append(f"  {i}. {rec}")
            
            text_lines.append(f"\n🔍 Top 5 đặc điểm nổi bật:")
            for feat_data in data['top_distinguishing_features']:
                feat = feat_data['feature']
                interp = feat_data['interpretation']
                z = feat_data['z_score']
                text_lines.append(f"  • {feat}: {interp} (z-score: {z:.2f})")
        
        text_lines.append("\n" + "="*80)
        text_lines.append("END OF REPORT")
        text_lines.append("="*80)
        
        text_path = output_path / 'cluster_profiles_report.txt'
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_lines))
        logger.info(f"  ✓ Saved: {text_path}")


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create sample data
    np.random.seed(42)
    data = {
        'userid': range(1, 101),
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100),
        'feature3': np.random.rand(100),
        'cluster': np.random.choice([0, 1, 2], 100)
    }
    df = pd.DataFrame(data)
    
    # Profile clusters
    profiler = ClusterProfiler(llm_provider='gemini')
    profiles = profiler.profile_all_clusters(df)
    profiler.save_profiles('test_output')
