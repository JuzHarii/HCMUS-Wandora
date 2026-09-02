# Wandora Design Theme

Wandora is a calm travel journal supported by practical planning tools. Its visual identity is warm, editorial, organized, and quietly intelligent.

| Document | Value |
| --- | --- |
| Status | Canonical theme foundation |
| Last updated | July 30, 2026 |
| Scope | Visual identity, design tokens, motion, accessibility, and content tone |
| Reference | `UI_Design_Assets/screen_00_design_theme.png` |
| Figma source | Pending shared file link |

This guide intentionally excludes detailed layouts, routes, and feature flows. The token values in this document are the source of truth until a shared Figma file is linked and matching variables are published.

## Design Direction

The interface should feel:

- Calm and low-pressure during long planning sessions.
- Warm and human, without becoming decorative or nostalgic.
- Editorial enough to feel rooted in travel.
- Structured enough to support group decisions.
- Helpful without making AI feel loud or separate from the product.

The visual language should suggest planning, reflection, shared context, and gentle guidance.

## Visual Principles

### Quiet Confidence

Use clear hierarchy, restrained contrast, and generous but purposeful spacing. Reliability should come from consistency rather than visual weight.

### Travel Journal Warmth

Use paper-like neutrals, natural greens, destination photography, and subtle route-inspired graphics. The result should feel curated rather than templated.

### Practical Collaboration

Selected, pending, confirmed, missing, and assigned states must be easy to distinguish. State is communicated through text, shape, and iconography as well as color.

### Calm AI Presence

AI assistance belongs inside the planning system. Use pale sage surfaces, compact summaries, and direct actions. Avoid sparkles, neon effects, and language that makes AI sound magical.

### One Signature

Wandora's signature visual is the journey line: a restrained route motif connecting places, decisions, or progress. Use it where it communicates movement or sequence, not as general decoration.

## Token Rules

- Use the named tokens in this document instead of introducing one-off values.
- Choose semantic tokens by purpose, not by whichever color looks closest.
- A component may introduce a new token only when an existing token cannot express a recurring need.
- New tokens must include a name, value, purpose, and accessibility check.
- Use CSS pixels for dimensions and `rem` for typography in implementation.

## Color

The foundation colors are sampled from the approved design reference. Warm neutrals carry the interface, forest green carries actions, and destination imagery provides natural color variation.

### Foundation Colors

| Token | Value | Purpose |
| --- | --- | --- |
| `color-canvas` | `#F6F5EF` | Main warm-paper background |
| `color-surface` | `#FFFCF8` | Cards, forms, menus, and raised content |
| `color-ink` | `#24312B` | Headings and primary text |
| `color-ink-muted` | `#5E6B65` | Supporting text and metadata |
| `color-brand` | `#315C4B` | Primary actions, selected emphasis, and focus |
| `color-brand-hover` | `#274A3D` | Hover state for primary actions |
| `color-brand-pressed` | `#1F3A31` | Pressed state for primary actions |
| `color-sage` | `#E8EFE9` | AI assistance and calm selected surfaces |
| `color-moss` | `#718B72` | Progress, route markers, and decorative emphasis |
| `color-sand` | `#D8C7A5` | Avatars, secondary markers, and warm emphasis |
| `color-route-blue` | `#C9DDE0` | Maps, travel information, and cool visual balance |
| `color-border-subtle` | `#D8D0C2` | Decorative dividers and surface boundaries |
| `color-border-strong` | `#7A867F` | Input and control boundaries that must remain visible |
| `color-on-brand` | `#FFFFFF` | Text and icons on brand-colored surfaces |

Do not use `color-moss`, `color-sand`, or `color-border-subtle` for normal text. They are supporting colors and do not provide dependable text contrast on every surface.

### Semantic Colors

Semantic colors communicate meaning and must not be replaced with brand colors.

| Meaning | Surface | Text and icon | Typical use |
| --- | --- | --- | --- |
| Success | `#E6F2EA` | `#2E684B` | Confirmed, complete, available |
| Warning | `#F5EDD8` | `#715A25` | Needs attention, incomplete |
| Danger | `#F7E6E3` | `#8A3F3C` | Error, destructive action, conflict |
| Information | `#E4EFF1` | `#315F68` | Travel detail, neutral notice |

Every semantic pair meets at least a `4.5:1` text contrast ratio. Always include a written label or recognizable icon so meaning never depends on hue alone.

### Color Balance

- Warm neutrals should occupy most of the interface.
- Forest green should remain concentrated around actions and important states.
- Sage supports AI and selection but should not cover entire views.
- Route blue provides a quiet cool counterpoint for travel and map information.
- Destination photography may introduce broader color, but UI chrome remains within the token palette.
- Avoid introducing additional accent colors for decoration alone.

## Typography

Typography combines an editorial travel voice with a highly readable planning interface.

### Font Families

| Role | Family | Weights |
| --- | --- | --- |
| Editorial | Cormorant Garamond, Georgia, "Times New Roman", serif | `600` |
| Interface | Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif | `400`, `500`, `600` |

Cormorant Garamond is reserved for the Wandora wordmark and expressive editorial headings. Inter is used for all controls, body copy, labels, metadata, and dense planning information.

Do not synthesize unavailable font weights. Use `font-synthesis: none` in the application.

### Type Scale

| Token | Size / line height | Weight | Use |
| --- | --- | --- | --- |
| `type-caption` | `12px / 16px` | `500` | Timestamps and compact metadata |
| `type-label` | `13px / 18px` | `600` | Form labels, tabs, and compact controls |
| `type-body-sm` | `14px / 20px` | `400` | Secondary copy and dense information |
| `type-body` | `16px / 24px` | `400` | Default body copy and inputs |
| `type-title-sm` | `20px / 28px` | `600` | Card and panel headings |
| `type-title-md` | `28px / 36px` | `600` | Major content headings |
| `type-display` | `48px / 52px` | `600` | Rare editorial statements |

Rules:

- Letter spacing is `0` for all text.
- Use sentence case for headings, labels, and controls.
- Keep normal body text at `16px` when reading comfort matters.
- Never scale font size continuously with viewport width.
- On smaller viewports, step `type-display` down to `40px / 44px`.
- Do not use the editorial font inside buttons, inputs, tables, or compact panels.
- Limit body copy to a comfortable reading width when it becomes paragraph-length.

## Spacing

All spacing follows a four-pixel base grid.

| Token | Value | Typical use |
| --- | --- | --- |
| `space-1` | `4px` | Tight icon and label relationships |
| `space-2` | `8px` | Compact control gaps |
| `space-3` | `12px` | Related content within a group |
| `space-4` | `16px` | Default component padding |
| `space-5` | `24px` | Card padding and group separation |
| `space-6` | `32px` | Major panel separation |
| `space-7` | `48px` | Section rhythm |
| `space-8` | `64px` | Large editorial breathing room |

Use the smallest token that preserves clarity. Compact planning information is allowed when labels, alignment, and grouping remain easy to scan.

## Shape And Elevation

The shape language is approachable and restrained. Large surfaces carry more rounding than compact controls.

### Radius

| Token | Value | Use |
| --- | --- | --- |
| `radius-xs` | `4px` | Progress tracks and small indicators |
| `radius-sm` | `8px` | Tooltips and compact utility surfaces |
| `radius-md` | `12px` | Inputs, menus, and standard controls |
| `radius-lg` | `20px` | Standard cards and panels |
| `radius-xl` | `28px` | Prominent editorial surfaces |
| `radius-pill` | `999px` | Buttons, chips, avatars, and segmented states |

Use `radius-lg` as the default card radius. Reserve `radius-xl` for a small number of visually prominent surfaces.

### Border And Shadow

| Token | Value | Use |
| --- | --- | --- |
| `border-subtle` | `1px solid #D8D0C2` | Surface separation |
| `border-control` | `1px solid #7A867F` | Inputs and interactive boundaries |
| `shadow-soft` | `0 2px 8px rgba(36, 49, 43, 0.06)` | Lightly raised interactive surfaces |
| `shadow-overlay` | `0 12px 32px rgba(36, 49, 43, 0.12)` | Menus, dialogs, and temporary overlays |

Borders should provide most separation. Do not add a shadow to every card, and do not stack multiple shadows.

## Controls And States

### Buttons

- Primary buttons use `color-brand` with `color-on-brand`.
- Primary hover and pressed states use the corresponding brand state tokens.
- Secondary buttons use `color-surface`, `color-brand`, and `border-control`.
- Destructive buttons use the danger semantic pair, not brand green.
- Default control height is `40px`; important touch actions should be at least `44px`.
- Compact controls may be `32px` high only when they are not the sole touch target and retain sufficient spacing.
- Labels use a clear verb and keep the same wording through confirmation or error feedback.

### Selection

- Selected states use `color-sage`, brand-colored text, and a visible icon, label, or border.
- Hover and selected states must remain visually distinct.
- Disabled states reduce emphasis but keep text readable. Do not communicate disabled state through opacity alone.

### Cards

Cards represent one object, decision, summary, or task. They should contain a clear title, concise metadata, visible status when relevant, and one obvious next action.

Do not nest cards. Use spacing, dividers, rows, or a soft background band for structure inside a card.

### Progress And Status

- Use thin progress tracks with `radius-pill`.
- Use determinate progress whenever completion can be measured.
- Pair status color with a label such as `Draft`, `Missing`, `Confirmed`, or `Needs review`.
- Use consistent wording for the same state throughout the product.
- Do not use decorative percentages or progress bars when no real progress exists.

## Iconography

- Use Lucide icons when an appropriate symbol exists.
- Standard icon sizes are `16px`, `18px`, and `20px`.
- Use a consistent `1.75px` stroke weight.
- Icons inherit the text color of their control unless a semantic state requires otherwise.
- Icon-only controls require an accessible name and a visible tooltip on hover or keyboard focus.
- Do not use an icon when a short text label is clearer.
- Do not mix filled and outline icon styles within the same context.

## Photography And Illustration

Destination photography provides emotional context and prevents the neutral green palette from becoming visually flat.

Photography should:

- Show the actual destination, activity, food, or travel context.
- Prefer natural daylight, believable color, and editorial composition.
- Remain clear enough to inspect without heavy overlays or aggressive cropping.
- Support the nearby content rather than act as generic decoration.
- Use consistent corner radii and image treatment.

Avoid dark stock-style travel photos, artificial saturation, heavy blur, and images that could represent any destination.

Illustration should remain minimal and functional:

- Route lines and waypoint markers.
- Simplified destination or map blocks.
- Member markers and shared-decision indicators.
- Journal-inspired fragments that support real information.

Avoid decorative blobs, generic travel clip art, and visual motifs that do not communicate content.

## AI Styling

AI assistance should look like a calm part of the planning system:

- Use `color-sage` for the main assistance surface.
- Keep summaries short and structured.
- Show extracted details in simple rows.
- Show uncertainty or missing information directly.
- Provide explicit actions for accepting, editing, retrying, or dismissing output.
- Identify generated suggestions in text when their origin matters.

Do not use sparkles, neon gradients, glowing borders, typing theatrics, or exaggerated claims.

## Motion

Motion should make Wandora feel responsive, connected, and calm. It must explain change, preserve context, or acknowledge input. Animation that serves no interaction or narrative purpose should be removed.

### Motion Tokens

| Token | Value | Use |
| --- | --- | --- |
| `motion-instant` | `80ms` | Pressed feedback and immediate state response |
| `motion-fast` | `140ms` | Hover, focus-adjacent color, and icon changes |
| `motion-loading-delay` | `150ms` | Delay before showing a loading indicator |
| `motion-base` | `220ms` | Menus, toggles, tabs, and small transitions |
| `motion-min-visible` | `300ms` | Minimum visible time for a shown loading indicator |
| `motion-slow` | `360ms` | Dialogs, drawers, and larger state changes |
| `motion-reveal` | `520ms` | Scroll and entry reveals |
| `motion-spin` | `900ms` | Continuous spinner rotation |
| `motion-loading` | `1200ms` | Repeating loading pulse |
| `motion-stagger` | `60ms` | Delay between related revealed items |
| `ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | Most state transitions |
| `ease-enter` | `cubic-bezier(0.16, 1, 0.3, 1)` | Elements entering or settling |
| `ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving |
| `ease-linear` | `linear` | Continuous rotation or determinate progress |

Use these tokens consistently. Do not create a custom duration or easing for an individual component without a recurring, documented reason.

### Hover And Press

- Animate color, border color, opacity, shadow, or transform using `motion-fast`.
- Buttons may darken on hover; they should not jump or noticeably change size.
- Interactive cards may move up by at most `1px` and adopt `shadow-soft`.
- Pressed controls may use `transform: scale(0.98)` for `motion-instant`.
- Keep the clickable area stable during animation.
- Never animate text size, letter spacing, width, or height on hover.

### Scroll Animation

Scroll animation should create rhythm without delaying access to content.

- Reveal meaningful groups, not every heading, icon, and paragraph.
- Use opacity from `0` to `1` with vertical movement from `12px` to `0`.
- Use `motion-reveal` with `ease-enter`.
- Trigger once when roughly 15 percent of the element enters the viewport.
- Stagger related items with `motion-stagger`, with no more than four staggered items in one group.
- Keep content visible by default before JavaScript initializes.
- Do not use scroll hijacking, scroll-linked parallax, or motion that competes with reading.

### Loading Animation

Choose the loading treatment that best describes the wait:

- Use determinate progress when progress is measurable.
- Use a compact spinner for a short action with no useful preview.
- Use skeletons when the final content structure is known.
- Use a soft opacity pulse between `0.65` and `1` over `motion-loading`.
- Delay loading indicators with `motion-loading-delay` to avoid flashing during instant responses.
- Once shown, keep an indicator visible for `motion-min-visible` to avoid flicker.
- Announce meaningful loading and completion states to assistive technology.
- Do not show multiple competing loading animations in the same region.

Continuous spinners use `motion-spin` with `ease-linear`. Skeletons should pulse rather than use a fast sweeping shimmer.

### Entry, Exit, And Overlays

- Entering overlays use opacity and up to `8px` of movement with `motion-slow` and `ease-enter`.
- Exiting overlays use `motion-base` with `ease-exit`.
- Toasts and temporary messages use `motion-base`; they do not bounce.
- Background dimming fades with the overlay and must not flash.
- Focus moves only after the destination element is present and remains visible.

### Motion Performance

- Prefer `transform` and `opacity`.
- Avoid animating `width`, `height`, `top`, `left`, or large shadows.
- Use `will-change` only shortly before a known animation and remove it afterward.
- Keep one-time interface animation below `700ms`.
- Repeating animation is reserved for loading or real ongoing activity.
- Test motion on lower-powered mobile devices, not only desktop hardware.

### Reduced Motion

When `prefers-reduced-motion: reduce` is active:

- Remove translation, scaling, parallax, and stagger.
- Replace entry and exit motion with an immediate state change or a short opacity fade.
- Stop decorative and repeating animation.
- Keep loading state understandable through static indicators and text.
- Use automatic scrolling only when required to reveal the result of the user's own action.
- Set smooth scrolling to `auto`.

Focus indicators, progress meaning, and state feedback must remain available when motion is reduced.

## Accessibility

Wandora targets WCAG 2.2 Level AA.

### Contrast

- Normal text must reach at least `4.5:1` against its background.
- Large text must reach at least `3:1`.
- Controls, icons, focus indicators, and meaningful graphics must reach at least `3:1` against adjacent colors.
- Placeholder text is not a substitute for a label and must remain readable.
- Validate every new color pair before it becomes a token.

### Keyboard And Focus

- Every interactive element must be reachable and usable by keyboard.
- Use a visible `2px` `color-brand` focus ring with a `2px` offset.
- Do not remove the browser focus indicator unless an equally visible replacement is provided.
- Focus order must follow the visual and reading order.
- Sticky content and overlays must not obscure the focused element.
- Focus indicators appear immediately and are not animated.

### Targets And Labels

- Use at least `40 x 40px` for standard interactive targets.
- Prefer `44 x 44px` for primary touch actions.
- Never go below the WCAG AA minimum of `24 x 24px` without a documented spacing or inline-content exception.
- Every control requires an accessible name.
- Icon-only controls require an accessible name and tooltip; the icon itself may be hidden from assistive technology.
- Visible labels and accessible names must use the same action wording.

### Content And State

- Never use color alone to communicate status, selection, errors, or progress.
- Error messages state what happened and how to correct it.
- Dynamic status and loading messages use an appropriate live region without repeatedly interrupting the user.
- Images require useful alternative text when they communicate content and empty alternative text when decorative.
- Text must remain usable at 200 percent zoom and reflow without horizontal scrolling at narrow widths.
- Interfaces must remain understandable when custom fonts fail to load.

### Motion Safety

- Respect `prefers-reduced-motion`.
- Do not flash content more than three times per second.
- Do not make essential information available only through animation.
- Pause or remove non-essential motion that continues for more than five seconds.

## Content Tone

Wandora copy should be clear, warm, specific, calm, and actionable.

Good examples:

- "Turn scattered ideas into one shared trip plan."
- "Missing: exact arrival time"
- "Ask Wandora to refine this plan."
- "Keep mornings relaxed."

Rules:

- Use active voice and plain verbs.
- Name actions consistently from control to confirmation.
- Explain how to recover from errors.
- Keep labels short and helper text useful.
- Avoid hype-heavy AI claims, technical language, and generic phrases such as "supercharge your travel planning."

## What To Avoid

- Neon colors, heavy gradients, glassmorphism, and glowing AI effects.
- Decorative blobs, generic travel imagery, and purposeless visual effects.
- Undifferentiated density that hides hierarchy or makes actions hard to find.
- Empty whitespace that forces unnecessary scrolling without improving comprehension.
- A flat green-and-beige treatment with no photography, route blue, or semantic color.
- Nested cards and shadows on every surface.
- Arbitrary radius, spacing, color, or motion values outside the token system.
- Long animation sequences, bounce effects, scroll hijacking, and decorative parallax.
- UI text that explains controls whose meaning is already clear.

## Theme Summary

Wandora balances editorial warmth with planning clarity. Warm paper, forest green, destination imagery, measured typography, and restrained journey-line motifs give the product its identity. Consistent tokens and calm motion make the interface feel responsive without adding noise, while measurable accessibility rules keep that experience available to everyone.

## Standards References

- [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
- [Understanding target size minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum)
- [Understanding non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast)
- [Understanding focus visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible)
