# Frontend Design Skill — Spendly

## Overview

This skill provides design guidance and implementation patterns for the Spendly personal expense tracker. It establishes a cohesive visual language, interaction patterns, and component library to maintain consistency across all pages and features.

---

## Design System

### Color Palette

All colors are defined as CSS variables in static/css/style.css :root block. **Never hardcode hex values** — always reference variables.

**Primary Colors:**
- --ink: #0f0f0f (Text, dark elements)
- --ink-soft: #2d2d2d (Secondary text)
- --ink-muted: #6b6b6b (Tertiary text, labels)
- --ink-faint: #a0a0a0 (Disabled, hints)

**Background Colors:**
- --paper: #f7f6f3 (Page background)
- --paper-warm: #f0ede6 (Section backgrounds)
- --paper-card: #ffffff (Card backgrounds)

**Accent Colors:**
- --accent: #1a472a (Primary action, brand green)
- --accent-light: #e8f0eb (Light green for badges, highlights)
- --accent-2: #c17f24 (Secondary accent, warm orange)
- --accent-2-light: #fdf3e3 (Light orange for accents)

**Semantic Colors:**
- --danger: #c0392b (Errors, destructive actions)
- --danger-light: #fdecea (Light red backgrounds)
- --success: #2d6a4f (Success states, confirmations)
- --success-light: #eef5f1 (Light green backgrounds)

**Border Colors:**
- --border: #e4e1da (Default borders)
- --border-soft: #eeebe4 (Subtle dividers)

### Typography

**Display Font:** 'DM Serif Display', Georgia, serif
- Used for: page titles, hero headlines, large headings
- Weight: 400 (regular), 1 (italic for emphasis)
- Sizes: clamp(1.75rem, 3vw, 2.5rem) to 2rem for headings

**Body Font:** 'DM Sans', system-ui, sans-serif
- Used for: body text, buttons, forms, navigation
- Weights: 300 (light), 400 (regular), 500 (medium), 600 (bold)
- Base size: 1rem (16px); scale with clamp() for responsive sizing
- Line height: 1.6

### Spacing & Sizing

**Border Radius:**
- --radius-sm: 6px (Form inputs, small buttons)
- --radius-md: 12px (Cards, larger buttons)
- --radius-lg: 20px (Hero cards, featured sections)

**Max Widths:**
- --max-width: 1200px (Page content container)
- --auth-width: 440px (Auth form container)

### Responsive Breakpoints

- @media (max-width: 900px) — Tablet/smaller desktop
- @media (max-width: 600px) — Mobile

---

## Component Patterns

### Navigation Bar

**Location:** templates/base.html, .navbar class  
**Usage:** Sticky top bar, visible on all pages

Rules:
- Always use url_for() for all links — never hardcode URLs
- Brand icon uses var(--accent) color
- Links are var(--ink-muted) by default, var(--ink) on hover
- CTA button (.nav-cta) uses var(--ink) background with var(--paper) text
- Conditional logic: show different links based on session.user_id

### Page Structure

All pages follow a three-layer structure:

1. **Hero/Header Section**
   - Centered, max-width container
   - Large display heading (DM Serif Display, clamp font size)
   - Supporting subtitle or description

2. **Content Card(s)**
   - background: var(--paper-card)
   - border: 1px solid var(--border)
   - border-radius: var(--radius-md)
   - padding: 2rem
   - box-shadow: 0 8px 40px rgba(0,0,0,0.06)

3. **Footer**
   - Black background (var(--ink))
   - White text (var(--paper))
   - Center-aligned, flex column

### Form Components

**Form Group (.form-group)**
- Margin bottom: 1.25rem
- Label: 0.85rem, font-weight 500, var(--ink-soft) color

**Form Input (.form-input)**
- Width: 100%
- Padding: 0.6rem 0.875rem
- Border: 1px var(--border)
- Focus: border-color changes to var(--accent)

**Submit Button (.btn-submit)**
- Width: 100%
- Padding: 0.7rem
- Background: var(--ink) (default), var(--accent) (hover)
- Transition: 0.2s background

### Button Styles

**Primary Button (.btn-primary)**
- Display: inline-block
- Background: var(--ink), hover: var(--accent)
- Color: var(--paper) text
- Padding: 0.65rem 1.5rem

**Ghost Button (.btn-ghost)**
- Background: transparent
- Border: 1px var(--border)
- Color: var(--ink-soft), hover: var(--ink)

### Auth Page Layout

Location: templates/login.html, templates/register.html

Structure:
- .auth-section: center vertically and horizontally
- .auth-container: max-width var(--auth-width) (440px)
- .auth-title: 2rem, DM Serif Display
- .auth-subtitle: 0.9rem, var(--ink-muted)

### Dashboard/Profile Layout

Location: templates/profile.html

Components:
- .profile-card: Account info and summary stats
- .info-row: Grid 100px / 1fr
- .summary-stats: Grid 1fr / 1fr (two stat boxes)
- .stat-box: Centered, light background
- .expenses-card: List of recent expenses
- .expense-row: Grid layout
- .empty-state: Dashed border, centered message

---

## Consistency Rules

### DO:
✅ Use CSS variables for all colors, spacing, typography  
✅ Use url_for() for all internal links  
✅ Use Jinja filters for currency formatting  
✅ Use vanilla JS only (no jQuery, no npm packages)  
✅ Extend base.html on every template  
✅ Use semantic HTML  
✅ Test on desktop (900px+) and mobile (600px) breakpoints  

### DON'T:
❌ Hardcode hex colors  
❌ Use inline <style> tags  
❌ Use CSS frameworks  
❌ Use JS frameworks  
❌ Add new external dependencies  

---

**Last Updated:** 2026-07-09  
**Version:** 1.0
