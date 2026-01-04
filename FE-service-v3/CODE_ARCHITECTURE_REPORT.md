# BÁO CÁO KIẾN TRÚC VÀ PHONG CÁCH CODE - FE-SERVICE-V3

**Phiên bản:** 0.1.0  
**Ngày tạo:** 04/01/2026  
**Mục đích:** Tài liệu hướng dẫn AI hiểu và phát triển thêm tính năng mới

---

## 📋 TỔNG QUAN DỰ ÁN

### Mục tiêu
Ứng dụng **Moodle Adaptive Learning Dashboard** - Giao diện học tập thích ứng tích hợp với Moodle LMS, hỗ trợ AI phân tích và cá nhân hóa trải nghiệm học tập cho học sinh và giáo viên.

### Công nghệ chính
- **Framework:** React 18.3.1 với TypeScript
- **Build Tool:** Vite 6.3.5
- **Styling:** TailwindCSS 3.4.17
- **UI Components:** Radix UI + shadcn/ui
- **Animation:** Motion (Framer Motion fork)
- **Charts:** Recharts 2.15.2
- **State Management:** React Hooks (useState, useEffect)

---

## 🏗️ KIẾN TRÚC THƯ MỤC

```
FE-service-v3/
├── src/
│   ├── components/           # Component chính
│   │   ├── ui/              # UI primitives (shadcn/ui)
│   │   ├── student/         # Components dành cho học sinh
│   │   ├── teacher/         # Components dành cho giáo viên
│   │   ├── figma/           # Components từ Figma design
│   │   ├── Header.tsx       # Header toàn cục
│   │   └── Sidebar.tsx      # Sidebar navigation
│   ├── services/            # API services
│   │   └── moodleApi.ts    # Tích hợp Moodle Web Services
│   ├── types/               # TypeScript type definitions
│   │   └── moodle.ts       # Moodle API types
│   ├── utils/               # Utility functions
│   │   └── ltiParams.ts    # LTI 1.3 parameter parser
│   ├── styles/              # Global styles
│   │   └── globals.css     # Styles bổ sung
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── index.css            # TailwindCSS + CSS variables
├── public/                  # Static assets
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
├── package.json             # Dependencies
├── Dockerfile               # Docker configuration
└── docker-compose.yml       # Docker compose setup
```

### Nguyên tắc tổ chức file

1. **Component hierarchy:** UI primitives → Feature components → Page components
2. **Separation of concerns:** Services, types, utils được tách riêng
3. **Role-based organization:** student/ và teacher/ folders cho từng vai trò
4. **Reusability:** UI components trong `ui/` có thể tái sử dụng toàn dự án

---

## 🎨 HỆ THỐNG MÀU SẮC VÀ THEME

### Color Palette (CSS Variables)

#### Light Mode (`:root`)
```css
--background: 0 0% 100%;           /* Trắng thuần */
--foreground: 222.2 84% 4.9%;      /* Đen xanh đậm */
--primary: 142 76% 36%;             /* Xanh lá chính (#16A34A) */
--primary-foreground: 144 62% 98%; /* Trắng xanh nhạt */
--secondary: 210 40% 96.1%;         /* Xám xanh nhạt */
--muted: 210 40% 96.1%;             /* Xám nhạt */
--accent: 210 40% 96.1%;            /* Xanh nhạt accent */
--destructive: 0 84.2% 60.2%;      /* Đỏ cảnh báo */
--border: 214.3 31.8% 91.4%;       /* Border xám nhạt */
--card: 0 0% 100%;                  /* Card nền trắng */
```

#### Dark Mode (`.dark`)
```css
--background: 222.2 84% 4.9%;      /* Đen xanh đậm */
--foreground: 210 40% 98%;          /* Trắng */
--primary: 142 76% 36%;             /* Xanh lá giữ nguyên */
--secondary: 217.2 32.6% 17.5%;     /* Xám xanh đậm */
--muted: 217.2 32.6% 17.5%;         /* Xám đậm */
--destructive: 0 62.8% 30.6%;      /* Đỏ đậm */
--border: 217.2 32.6% 17.5%;       /* Border xám đậm */
--card: 222.2 84% 4.9%;             /* Card nền tối */
```

#### Chart Colors
```css
--chart-1: 142 76% 36%;   /* Xanh lá chính */
--chart-2: 160 84% 39%;   /* Xanh lá tươi */
--chart-3: 291 64% 42%;   /* Tím */
--chart-4: 142 71% 45%;   /* Xanh lá nhạt */
--chart-5: 160 60% 45%;   /* Xanh lục nhạt */
```

### Semantic Color Usage

| Màu | Mục đích | Ví dụ sử dụng |
|-----|----------|---------------|
| `primary` | Actions, links, highlights | Buttons, active states |
| `secondary` | Secondary actions, hover states | Sidebar hover, cards |
| `muted` | Disabled states, less important text | Placeholders, descriptions |
| `destructive` | Errors, warnings, delete actions | Error messages, delete buttons |
| `accent` | Highlights, notifications | Badges, notification dots |

### Border Radius System
```javascript
--radius: 1rem;                    /* Base: 16px */
lg: 'var(--radius)',               /* 16px */
md: 'calc(var(--radius) - 2px)',  /* 14px */
sm: 'calc(var(--radius) - 4px)',  /* 12px */
xs: 'calc(var(--radius) - 6px)',  /* 10px */
```

**Quy tắc:** Sử dụng `rounded-xl` (12px) cho hầu hết components, `rounded-2xl` (16px) cho cards lớn.

---

## 🧩 HỆ THỐNG COMPONENT

### UI Primitives (shadcn/ui)

Tất cả components trong `src/components/ui/` follow shadcn/ui pattern:

#### 1. Button Component
```typescript
// Pattern: Variant-based styling với CVA (Class Variance Authority)
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2...",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-white...",
        outline: "border bg-background...",
        secondary: "bg-secondary...",
        ghost: "hover:bg-accent...",
        link: "text-primary underline-offset-4..."
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md gap-1.5 px-3",
        lg: "h-10 rounded-md px-6",
        icon: "size-9 rounded-md"
      }
    }
  }
);
```

**Cách sử dụng:**
```tsx
<Button variant="default" size="lg">Click me</Button>
<Button variant="ghost" size="icon"><Icon /></Button>
```

#### 2. Card Component
```typescript
// Pattern: Composition pattern với data-slot
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content here</CardContent>
  <CardFooter>Footer actions</CardFooter>
</Card>
```

**Styling:** Cards có `rounded-xl`, `border`, và `bg-card` mặc định.

#### 3. Typography
- **Font:** Inter (Google Fonts)
- **Weights:** 300, 400, 500, 600, 700
- **Base text:** `text-foreground`
- **Muted text:** `text-muted-foreground`

### Feature Components

#### StudentDashboard
**Location:** `src/components/student/StudentDashboard.tsx`

**Chức năng:**
- Hiển thị tiến độ học tập cá nhân
- Biểu đồ phân tích kỹ năng (Radar Chart)
- Learning path với trạng thái (completed, in-progress, locked)
- Activity heatmap (7 ngày)

**Data Flow:**
```
1. useEffect() → fetchDashboardData()
2. getLtiParams() → Extract user/course from URL
3. Moodle API calls → getSiteInfo, getUserCourses, getStudentProgress
4. setState() → Update UI
5. Fallback to mock data if API fails
```

**Key Patterns:**
```typescript
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState(mockData); // Always have fallback

useEffect(() => {
  async function fetch() {
    try {
      const realData = await apiCall();
      setData(realData);
    } catch (err) {
      console.error(err);
      // Keep using mockData
    } finally {
      setLoading(false);
    }
  }
  fetch();
}, []);
```

#### TeacherDashboard
**Location:** `src/components/teacher/TeacherDashboard.tsx`

**Chức năng:**
- Tổng quan lớp học (total students, active today)
- Biểu đồ hiệu suất lớp (Bar Chart)
- Activity trend (Line Chart)
- Completion distribution (Pie Chart)
- Struggling topics identification

**Số liệu hiển thị:**
- Total Students
- Active Today
- Average Completion %
- Most Popular Topic

#### StudentList
**Location:** `src/components/teacher/StudentList.tsx`

**Chức năng:**
- Danh sách học sinh với search và filter
- Progress tracking per student
- Activity level indicators (high/medium/low)
- Trend arrows (up/down/stable)
- Student detail modal với AI insights

**UI Patterns:**
- Table với Avatar, Progress bar, Badges
- Search input với debounce
- Filter dropdown (activity level)
- Modal dialog cho chi tiết

#### CourseAnalytics
**Location:** `src/components/teacher/CourseAnalytics.tsx`

**Chức năng:**
- Module views analysis (Bar Chart)
- Resource type distribution (Pie Chart)
- Top performers leaderboard
- Weekly engagement tracking

---

## 🔌 TÍCH HỢP API

### Moodle Web Services Integration

**File:** `src/services/moodleApi.ts`

#### Configuration
```typescript
const MOODLE_URL = import.meta.env.VITE_MOODLE_URL || "";
const MOODLE_TOKEN = import.meta.env.VITE_MOODLE_TOKEN || "";
```

**Environment Variables (.env):**
```env
VITE_MOODLE_URL=https://your-moodle-site.com
VITE_MOODLE_TOKEN=your_secret_token
```

#### Generic API Call Pattern
```typescript
async function callMoodleApi<T>(
  wsfunction: string,
  params: MoodleApiParams = {}
): Promise<T> {
  const url = new URL(`${MOODLE_URL}/webservice/rest/server.php`);
  url.searchParams.append("wstoken", MOODLE_TOKEN);
  url.searchParams.append("wsfunction", wsfunction);
  url.searchParams.append("moodlewsrestformat", "json");
  
  // Add params...
  const response = await fetch(url.toString());
  const data = await response.json();
  
  if (data.exception || data.errorcode) {
    throw new Error(data.message);
  }
  return data;
}
```

#### Key API Functions

| Function | Web Service | Mục đích |
|----------|-------------|----------|
| `getSiteInfo()` | `core_webservice_get_site_info` | User info & site config |
| `getUserCourses(userId)` | `core_enrol_get_users_courses` | Courses của user |
| `getEnrolledUsers(courseId)` | `core_enrol_get_enrolled_users` | Danh sách học sinh |
| `getCourseContent(courseId)` | `core_course_get_contents` | Nội dung khóa học |
| `getCourseCompletion(courseId, userId)` | `core_completion_get_activities_completion_status` | Completion status |
| `getStudentProgress(courseId, userId)` | Custom logic | Tính toán progress % |

#### Error Handling Pattern
```typescript
try {
  const data = await moodleApiFunction();
  setData(data);
} catch (error) {
  console.error("Moodle API Error:", error);
  // Fallback to mock data (không show error cho user)
  setData(mockData);
}
```

**Triết lý:** Graceful degradation - app vẫn hoạt động với mock data nếu API fail.

### LTI 1.3 Integration

**File:** `src/utils/ltiParams.ts`

#### URL Parameters
```typescript
interface LtiParams {
  userId: number;              // user_id
  userFullName: string;        // lis_person_name_full
  userEmail: string;           // lis_person_contact_email_primary
  roles: string[];             // roles (parsed array)
  userRole: 'STUDENT' | 'INSTRUCTOR' | 'ADMINISTRATOR' | 'UNKNOWN';
  courseId: number;            // context_id
  courseTitle: string;         // context_title
  resourceLinkId: number;      // resource_link_id
  toolConsumerInstanceGuid: string;
}
```

#### Usage Pattern
```typescript
const ltiParams = getLtiParams();

if (ltiParams) {
  const userId = ltiParams.userId;
  const courseId = ltiParams.courseId;
  // Use LTI data
} else {
  // Fallback to default or demo mode
  const userId = 2; // Default student
}
```

---

## 🎭 ANIMATION VÀ TRANSITIONS

### Motion (Framer Motion)

**Library:** `motion` (modern fork of Framer Motion)

#### Page Transitions
```typescript
<AnimatePresence mode="wait">
  <motion.div
    key={`${userRole}-${currentPage}`}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    transition={{ duration: 0.2 }}
  >
    {content}
  </motion.div>
</AnimatePresence>
```

**Pattern:**
- `mode="wait"`: Đợi exit animation xong mới chạy enter
- `key`: Force remount khi role/page thay đổi
- `initial → animate → exit`: Lifecycle của animation

#### Card Animations
```typescript
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.4, delay: index * 0.1 }}
>
  <Card>...</Card>
</motion.div>
```

**Stagger effect:** `delay: index * 0.1` tạo hiệu ứng cascade.

### CSS Transitions

All components có `transition-all` hoặc `transition-colors`:
```css
transition-all        /* Smooth all properties */
transition-colors     /* Only colors */
duration-300          /* 300ms (default) */
```

---

## 📊 CHARTS VÀ DATA VISUALIZATION

### Recharts Configuration

**Library:** `recharts@2.15.2`

#### Line Chart (Progress over time)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={progressData}>
    <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
    <XAxis dataKey="week" />
    <YAxis />
    <Tooltip />
    <Line 
      type="monotone" 
      dataKey="score" 
      stroke="hsl(var(--primary))" 
      strokeWidth={2}
    />
  </LineChart>
</ResponsiveContainer>
```

**Key Points:**
- `ResponsiveContainer`: Auto-resize
- `strokeDasharray="3 3"`: Dashed grid
- `stroke="hsl(var(--primary))"`: Use CSS variable

#### Radar Chart (Skills analysis)
```tsx
<RadarChart data={skillsData}>
  <PolarGrid />
  <PolarAngleAxis dataKey="skill" />
  <PolarRadiusAxis angle={90} domain={[0, 100]} />
  <Radar 
    dataKey="value" 
    stroke="hsl(var(--primary))" 
    fill="hsl(var(--primary))"
    fillOpacity={0.5}
  />
</RadarChart>
```

#### Pie Chart (Distribution)
```tsx
<PieChart>
  <Pie
    data={completionData}
    dataKey="value"
    nameKey="name"
    cx="50%"
    cy="50%"
    innerRadius={60}
    outerRadius={80}
  >
    {completionData.map((entry, index) => (
      <Cell key={index} fill={entry.color} />
    ))}
  </Pie>
</PieChart>
```

**Pattern:** Custom colors per data entry với `Cell`.

#### Bar Chart (Class performance)
```tsx
<BarChart data={classPerformanceData}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="name" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="score" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
</BarChart>
```

**Styling:** `radius={[8, 8, 0, 0]}` bo tròn góc trên.

---

## 🎯 STATE MANAGEMENT VÀ DATA FLOW

### Pattern: Local State with Hooks

**Không sử dụng:** Redux, Zustand, Context API  
**Lý do:** App đơn giản, không cần global state

#### State Organization
```typescript
// Loading & Error states
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

// Data states với fallback
const [users, setUsers] = useState(mockUsers);
const [courses, setCourses] = useState(mockCourses);

// UI states
const [searchTerm, setSearchTerm] = useState("");
const [selectedItem, setSelectedItem] = useState<Item | null>(null);
```

#### Data Fetching Pattern
```typescript
useEffect(() => {
  async function fetchData() {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiCall();
      setData(data);
    } catch (err) {
      console.error(err);
      setError(err.message);
      // Keep mock data
    } finally {
      setLoading(false);
    }
  }
  
  fetchData();
}, [dependencies]);
```

### Props Drilling

**Current approach:** Props được pass qua 1-2 levels  
**Ví dụ:**
```
App → Header (darkMode, toggleDarkMode, userRole, userName)
App → Sidebar (userRole, currentPage, onNavigate, isOpen)
```

**Khi nào cần refactor:** Nếu props qua >3 levels → Consider Context.

---

## 📱 RESPONSIVE DESIGN

### Breakpoints (Tailwind)

```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

### Mobile-First Approach

#### Sidebar
```tsx
// Desktop: Always visible
// Mobile: Overlay with backdrop

<aside className={cn(
  "w-64 border-r bg-card",
  "md:translate-x-0",              // Desktop: visible
  "fixed md:relative",              // Mobile: fixed overlay
  isOpen ? "translate-x-0" : "-translate-x-full"  // Mobile: toggle
)}>
```

#### Header
```tsx
<Button className="md:hidden">   {/* Show only on mobile */}
  <Menu />
</Button>

<div className="hidden sm:block"> {/* Hide on mobile */}
  <h1>Title</h1>
</div>
```

### Common Patterns

| Pattern | Class | Usage |
|---------|-------|-------|
| Hide on mobile | `hidden md:block` | Desktop-only elements |
| Show on mobile | `md:hidden` | Mobile-only (menu button) |
| Stack on mobile | `flex-col md:flex-row` | Vertical → Horizontal |
| Grid responsive | `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` | Auto layout |

---

## 🧪 CODING CONVENTIONS

### TypeScript

#### Type Definitions
```typescript
// Interface for props
interface ComponentProps {
  title: string;
  count?: number;              // Optional
  onAction: () => void;         // Function
  items: Item[];                // Array
}

// Interface for data
interface Student {
  id: number;
  name: string;
  progress: number;
  activity: "high" | "medium" | "low";  // Union type
}
```

#### Type Imports
```typescript
import type { MoodleUser, MoodleCourse } from "../types/moodle";
```

**Quy tắc:** Dùng `type` import cho type-only imports.

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase | `StudentDashboard` |
| Files | PascalCase (components), camelCase (utils) | `Header.tsx`, `moodleApi.ts` |
| Functions | camelCase | `fetchDashboardData` |
| Constants | UPPER_SNAKE_CASE | `MOODLE_URL` |
| CSS Classes | kebab-case (Tailwind) | `bg-primary`, `rounded-xl` |
| State variables | camelCase | `[darkMode, setDarkMode]` |

### File Structure Convention

```typescript
// 1. Imports
import { useState } from "react";
import { Card } from "../ui/card";
import { apiFunction } from "../../services/api";

// 2. Types/Interfaces
interface Props {
  // ...
}

// 3. Constants (mock data, config)
const mockData = [...];

// 4. Component
export function Component({ props }: Props) {
  // 4a. State
  const [state, setState] = useState();
  
  // 4b. Effects
  useEffect(() => {}, []);
  
  // 4c. Handlers
  const handleClick = () => {};
  
  // 4d. Render helpers
  const renderItem = () => {};
  
  // 4e. JSX
  return <div>...</div>;
}
```

### JSX Patterns

#### Conditional Rendering
```tsx
{loading ? (
  <Skeleton />
) : error ? (
  <ErrorMessage />
) : (
  <Content />
)}

{/* Short circuit */}
{isVisible && <Component />}
```

#### List Rendering
```tsx
{items.map((item) => (
  <Card key={item.id}>
    {item.name}
  </Card>
))}
```

**Quy tắc:** Always provide `key` prop.

#### Styling với cn()
```tsx
import { cn } from "./ui/utils";

<div className={cn(
  "base-classes",
  isActive && "active-classes",
  isError && "error-classes",
  customClassName
)}>
```

**Pattern:** `cn()` merges Tailwind classes và resolves conflicts.

---

## 🔧 UTILITY FUNCTIONS

### cn() - Class Name Merger
```typescript
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**Usage:**
```tsx
cn("px-4 py-2", "px-6")  // Result: "px-6 py-2" (conflict resolved)
```

### getLtiParams() - LTI Parser
```typescript
const params = getLtiParams();

if (!params) {
  // Not in LTI context, use demo mode
}
```

**Returns:** `LtiParams | null`

---

## 🎨 DESIGN SYSTEM TOKENS

### Spacing Scale
```
0.5 = 2px
1   = 4px
2   = 8px
3   = 12px
4   = 16px
6   = 24px
8   = 32px
12  = 48px
16  = 64px
```

**Usage:** `p-4`, `mb-6`, `gap-3`

### Shadow System
```css
shadow-sm  : 0 1px 2px
shadow     : 0 1px 3px
shadow-md  : 0 4px 6px
shadow-lg  : 0 10px 15px
shadow-xl  : 0 20px 25px
shadow-2xl : 0 25px 50px
```

**Usage:** Buttons `shadow-2xl`, Cards `shadow-md`

### Icon Sizes
```tsx
<Icon className="h-4 w-4" />  {/* Small - 16px */}
<Icon className="h-5 w-5" />  {/* Default - 20px */}
<Icon className="h-6 w-6" />  {/* Large - 24px */}
```

**Library:** `lucide-react@0.487.0`

---

## 🚀 BUILD & DEPLOYMENT

### Development
```bash
npm run dev     # Start Vite dev server (port 5173)
```

### Production Build
```bash
npm run build   # Build to dist/
```

### Docker
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "run", "preview"]
```

**Port:** 4173 (preview), 5173 (dev)

---

## 📋 CHECKLIST PHÁT TRIỂN TÍNH NĂNG MỚI

### 1. Thêm Component Mới

- [ ] Tạo file trong folder phù hợp (`student/` hoặc `teacher/`)
- [ ] Follow naming convention: PascalCase
- [ ] Import types từ `types/moodle.ts` nếu cần
- [ ] Tạo mock data fallback
- [ ] Implement loading & error states
- [ ] Add animations với motion
- [ ] Responsive design (mobile-first)
- [ ] Add to navigation nếu cần (Sidebar)

### 2. Thêm API Function

- [ ] Định nghĩa type trong `types/moodle.ts`
- [ ] Thêm function vào `services/moodleApi.ts`
- [ ] Follow pattern: `callMoodleApi<Type>(wsfunction, params)`
- [ ] Document required Moodle capabilities
- [ ] Test với mock data trước
- [ ] Handle errors gracefully

### 3. Thêm UI Component

- [ ] Check nếu component đã có trong `ui/` (shadcn/ui)
- [ ] Nếu chưa có, copy từ [ui.shadcn.com](https://ui.shadcn.com)
- [ ] Customize colors với CSS variables
- [ ] Test dark mode
- [ ] Document props interface

### 4. Styling Guidelines

- [ ] Use Tailwind classes (không inline CSS)
- [ ] Use `cn()` cho conditional classes
- [ ] Follow spacing scale (4px increment)
- [ ] Use CSS variables cho colors
- [ ] Test responsive (mobile, tablet, desktop)
- [ ] Test dark mode

### 5. Testing

- [ ] Test với LTI params (có và không có)
- [ ] Test API success & failure cases
- [ ] Test loading states
- [ ] Test empty states
- [ ] Test dark mode
- [ ] Test responsive layouts
- [ ] Test animations

---

## 🔍 COMMON PATTERNS & ANTI-PATTERNS

### ✅ DO

```typescript
// Use semantic color variables
className="bg-primary text-primary-foreground"

// Fallback to mock data
const [data, setData] = useState(mockData);

// Conditional rendering với proper loading
{loading ? <Skeleton /> : <Content data={data} />}

// Type-safe props
interface Props {
  userId: number;
  onUpdate: (id: number) => void;
}

// Responsive classes
className="flex flex-col md:flex-row gap-4"
```

### ❌ DON'T

```typescript
// Hard-coded colors
className="bg-[#16A34A]"  // Use bg-primary instead

// No fallback data
const [data, setData] = useState(null);  // Add mockData

// Không handle loading
return <Content data={data} />  // May be undefined

// Any types
const data: any = await fetch()  // Define proper type

// Desktop-only design
className="grid grid-cols-3"  // Add mobile breakpoint
```

---

## 📚 DEPENDENCIES QUAN TRỌNG

### Core Libraries

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "motion": "*",
  "recharts": "^2.15.2"
}
```

### UI Components (Radix UI)

```json
{
  "@radix-ui/react-dialog": "^1.1.6",
  "@radix-ui/react-dropdown-menu": "^2.1.6",
  "@radix-ui/react-select": "^2.1.6",
  "@radix-ui/react-tooltip": "^1.1.8",
  // ... 20+ more Radix components
}
```

**Lưu ý:** Radix UI là unstyled components, được style bằng Tailwind.

### Styling

```json
{
  "tailwindcss": "^3.4.17",
  "autoprefixer": "^10.4.22",
  "postcss": "^8.5.6",
  "class-variance-authority": "^0.7.1",
  "clsx": "*",
  "tailwind-merge": "*"
}
```

### Development

```json
{
  "vite": "6.3.5",
  "@vitejs/plugin-react-swc": "^3.10.2",
  "@types/react": "^19.2.2",
  "typescript": "^5.x"
}
```

---

## 🎯 KIẾN TRÚC QUYẾT ĐỊNH

### Tại sao chọn Vite?
- ⚡ Fast HMR (Hot Module Replacement)
- 🔧 Out-of-box TypeScript support
- 📦 Optimized production builds
- 🌐 Modern ESM-based

### Tại sao chọn Radix UI + Tailwind?
- ♿ Accessibility out-of-box
- 🎨 Full styling control
- 📱 Responsive & mobile-friendly
- 🔧 Headless architecture (decoupled logic/UI)

### Tại sao không dùng Global State?
- 📊 Simple data flow (parent → child)
- 🔄 No data shared across routes
- 🚀 Easier to understand & debug
- 📉 Less boilerplate code

### Tại sao Mock Data Fallback?
- 🎯 Demo mode cho testing
- 🔒 Không require Moodle access để dev
- 🛡️ Graceful degradation
- 👨‍💻 Better DX (Developer Experience)

---

## 🐛 DEBUGGING TIPS

### Check LTI Params
```typescript
const ltiParams = getLtiParams();
console.log("LTI Parameters:", ltiParams);
```

**URL Example:**
```
?user_id=2&context_id=5&roles=Student&context_title=Python%20Course
```

### Check Moodle API
```typescript
console.log("Moodle URL:", import.meta.env.VITE_MOODLE_URL);
console.log("Token available:", !!import.meta.env.VITE_MOODLE_TOKEN);
```

### Check Component State
```typescript
useEffect(() => {
  console.log("Current state:", { loading, error, data });
}, [loading, error, data]);
```

### Inspect Network Requests
1. Open DevTools → Network
2. Filter: `webservice/rest/server.php`
3. Check request params & response

### Dark Mode Issues
```typescript
console.log("Dark mode:", document.documentElement.classList.contains('dark'));
```

---

## 📖 TÀI LIỆU THAM KHẢO

### Official Docs

- **React:** https://react.dev
- **Vite:** https://vitejs.dev
- **TailwindCSS:** https://tailwindcss.com
- **Radix UI:** https://radix-ui.com
- **Recharts:** https://recharts.org
- **Motion:** https://motion.dev
- **shadcn/ui:** https://ui.shadcn.com

### Moodle Integration

- **Moodle Web Services:** https://docs.moodle.org/dev/Web_services
- **LTI 1.3:** https://docs.moodle.org/en/LTI
- **Moodle API Functions:** https://docs.moodle.org/dev/Web_service_API_functions

### Internal Docs

- `MOODLE_INTEGRATION.md` - Setup guide
- `QUICKSTART.md` - Quick start
- `README.md` - Project overview

---

## 🎓 KẾT LUẬN

### Triết lý thiết kế

1. **User-First:** Học sinh và giáo viên là trung tâm
2. **AI-Enhanced:** AI insights ở mọi nơi (nhưng không xâm phạm)
3. **Graceful Degradation:** Hoạt động tốt cả khi API fail
4. **Mobile-Friendly:** Responsive từ đầu
5. **Accessibility:** ARIA labels, keyboard navigation
6. **Performance:** Fast load, smooth animations

### Hướng phát triển tương lai

- [ ] Thêm real-time notifications (WebSocket)
- [ ] AI chatbot integration
- [ ] Personalized learning recommendations
- [ ] Gamification (badges, achievements)
- [ ] Social features (study groups)
- [ ] Advanced analytics (ML-powered)
- [ ] Multi-language support (i18n)
- [ ] Progressive Web App (PWA)

### Lời kết

File này là **living document** - sẽ được update khi có thay đổi architecture hoặc conventions. Mọi developer/AI làm việc với codebase này nên đọc và tuân theo các guidelines trên để đảm bảo consistency.

**Version:** 1.0.0  
**Last Updated:** 04/01/2026  
**Maintainer:** Development Team

---

## 📞 LIÊN HỆ & HỖ TRỢ

Nếu có thắc mắc về architecture hoặc cần clarification:
1. Check code comments trong các files
2. Refer to official documentation
3. Review existing components for patterns
4. Ask team lead hoặc senior developers

**Happy Coding! 🚀**
