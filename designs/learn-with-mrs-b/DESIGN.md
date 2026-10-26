---
name: "learn-with-mrs-b"
version: "1.0.0"
description: "Calm, trustworthy, highly legible tutor back-office design system for Learn with Mrs. B."
colors: {"--bg": "#f8fafc", "--bg-alt": "#f1f5f9", "--panel": "#ffffff", "--panel-solid": "#ffffff", "--panel-hover": "#f8fafc", "--panel-sidebar": "#0f172a", "--panel-sidebar-hover": "#1e293b", "--text": "#0f172a", "--text-sidebar": "#f8fafc", "--muted": "#475569", "--muted-light": "#64748b", "--muted-sidebar": "#94a3b8", "--brand": "#0c7fac", "--brand-hover": "#0a6b92", "--brand-light": "#e0f2fe", "--accent": "#b45309", "--accent-hover": "#92400e", "--accent-gold": "#d97706", "--line": "#e2e8f0", "--line-strong": "#cbd5e1", "--line-sidebar": "#1e293b", "--focus": "#0c7fac", "--success": "#059669", "--success-light": "#ecfdf5", "--danger": "#b91c1c", "--danger-hover": "#991b1b", "--danger-light": "#fef2f2", "--warn": "#b45309", "--control-ink": "#ffffff"}
---

# learn-with-mrs-b

## referenceWorld

Warm educational publishing, bespoke British primary tutoring desk, quiet Montessori study atelier, and calm administrative concierge. Avoids cold clinical enterprise software or noisy SaaS dashboards in favor of a comforting, organized physical desk where a dedicated educator manages family relationships, lesson materials, and video sessions with clarity and dignity.

## antiPatterns

Reject decorative linear or radial gradients, blur glassmorphism, glowing neon borders, giant floating pill tabs, and fake animated waveforms. Eliminate low-contrast slate-on-slate text, unlabelled mystery-meat icons, ambiguous modal traps, destructive actions without confirmation guards, and high-stimulus gamification badges that create anxiety for non-technical educators.

## materiality

Crisp, opaque white cards (#ffffff) resting calmly upon a soothing slate-50 canvas (#f8fafc), framed by a grounding deep navy sidebar (#0f172a). Structural separation is defined by fine slate-200 dividers (#e2e8f0) and subtle slate-100 surfaces (#f1f5f9). Primary actions feature trustworthy brand blue (#0c7fac) with a darker pressed shade (#0a6b92), supported by warm educational gold accents (#b45309) for highlights and milestones.

## density

Relaxed, readable administrative density tailored for clear comprehension. Body text defaults to a comfortable 16px (1rem) with a 1.6 line height and a sustained reading measure capped near 65ch. Action cards, roster items, and registration panels maintain generous 1.5rem padding and 1.5rem cluster gaps. Negative space functions as a clear visual boundary between separate family records, preventing visual crowding while keeping critical contact and schedule details immediately scannable.

## motionGrammar

Deliberate, subtle motion transitions capped at 150ms using a smooth cubic-bezier(0.2, 0.8, 0.2, 1) curve. Transitions are restricted to functional feedback: modal open/close, accordion expansion, and button hover/active states. When prefers-reduced-motion is enabled, all animations, transitions, and transforms are immediately disabled to ensure absolute vestibular comfort.

## interactionPhysics

Direct, forgiving, and tactile interaction model. All primary buttons, select inputs, and filter chips provide a generous minimum touch target of 44px (2.75rem) with clear physical boundaries. Filter tabs toggle instantly without jarring layout shift. Destructive actions such as canceling a scheduled session require an explicit confirmation prompt. Interactive links and buttons provide high-contrast hover feedback and an immediate 2px focus ring on keyboard navigation.

## informationHierarchy

Strict editorial hierarchy guiding the tutor attention to urgent tasks first: 1. Pending registration applications from new families requiring approval or decline. 2. Imminent tutoring sessions with direct one-click Start Zoom triggers and student attendance status. 3. Active student rosters and lesson progress notes. 4. Teacher Studio lesson planning and administrative settings. Numerical counters (such as pending registrations count) use clear tabular badges that never obscure labels.

## responsiveBehavior

Adaptive layout transitioning seamlessly from widescreen desktop down to 320px mobile viewports. On desktop, the fixed 18rem navy sidebar anchors navigation beside a fluid, single-page work area capped at 80rem. Below 768px, the sidebar collapses into an accessible slide-over drawer triggered by an unmistakable hamburger button. Card grids reflow from multi-column rows into clean vertical stacks, while action button groups maintain full touch targets without horizontal clipping or overflow.

## Accessibility

Strict WCAG 2.1 AA compliance across all declared views and themes. Body text achieves at least 7.2:1 contrast against ground surfaces (slate-900 on white reaches 17.8:1, well above the 4.5:1 requirement). Secondary muted text achieves over 7.5:1. Interactive control ink on brand blue reaches 4.52:1. Focus indicators provide a high-contrast 2px solid outline with 3px offset meeting the 3:1 non-text contrast mandate. All interactive elements feature accessible labels, aria-expanded states, and full keyboard tab stops.

## brandVoice

Warm, encouraging, respectful, and crystal clear. Communication uses simple, reassuring educational terminology rather than technical software jargon: Registrations, Students, Schedule, Start Zoom, Lesson Editor. Notifications and error alerts state plainly what occurred and provide an immediate, self-explanatory recovery step without alarming or patronizing the educator.

## iconography

Consistent, clean monochrome line iconography drawn from Lucide React (LayoutDashboard, Users, Calendar, UserPlus, Video, Check, X, BookOpen, Settings, LogOut). Every icon is paired with an explicit, visible text label or accessible aria-label. Unaccompanied symbolic icons are strictly prohibited for actionable commands.

## dataViz

Clear, human-readable summary metric tiles for essential tutor numbers: Active Students, Hours Taught, Upcoming Sessions, and Pending Registrations. Numbers use large, legible bold numerals with baseline-aligned descriptive text labels. Data status is never communicated by color alone: status badges combine clear semantic text with distinct tonal backgrounds and boundary borders. Absent data is explicitly marked as No sessions scheduled rather than misleading zeroes.

## stateGrammar

Complete state grammar covering default, hover, active, focus-visible, disabled, loading, empty, success, and error conditions. Loading states feature a calm branded spinner with accessible status text. Empty states display a dashed slate-300 enclosure with an encouraging instructional message. Registration reviews clearly distinguish pending decisions from finalized archives. Schedule items clearly separate live upcoming sessions from canceled meetings.

## provenance

Derived from the real application code of the Learn with Mrs. B tutor back office (C:/Users/super/Outpost/lwmb-d1). Observed design tokens in globals.css, layout.tsx, registrations/page.tsx, and schedule/page.tsx provide the authoritative foundation for colors, typography, and component structures. Inferred ergonomic rules and touch target metrics adapt educational software best practices for non-technical tutors. Invented semantic token mappings harmonize the serene British tutoring aesthetic with strict NouGenDesigns v0 schema requirements.
