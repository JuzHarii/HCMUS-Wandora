import { useState, type ReactNode } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight, ArrowUpRight, CalendarDays, Check, ChevronRight, Clock3, Compass, ListChecks, MapPinned, Menu, UsersRound, WalletCards, X } from 'lucide-react'
import { motion } from 'motion/react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router'
import { z } from 'zod'

import { useAuth } from '@/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const waitlistSchema = z.object({
  name: z.string().min(2, 'Use at least 2 characters.'),
  email: z.string().email('Enter a valid email address.'),
})

type WaitlistValues = z.infer<typeof waitlistSchema>

const fadeUp = { hidden: { opacity: 0, y: 18 }, visible: { opacity: 1, y: 0 } }

export function LandingPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { user, logout } = useAuth()
  const closeMenu = () => setIsMenuOpen(false)

  return (
    <div className="min-h-screen overflow-x-hidden bg-canvas text-ink">
      <header className="site-header">
        <a className="wordmark" href="#top" onClick={closeMenu}>Wandora</a>
        <nav className="desktop-nav" aria-label="Main navigation"><a href="#product">Product</a><a href="#how-it-works">How it works</a><a href="#groups">For groups</a></nav>
        <div className="header-actions">
          {user ? <><Link className="signin-link" to="/home">My trips</Link><span className="account-name">Hi, {user.full_name.split(' ')[0]}</span><button className="signin-link logout-button" type="button" onClick={logout}>Sign out</button></> : <Link className="signin-link" to="/auth?mode=login">Sign in</Link>}
          <Link className="button button-primary header-cta" to="/trips/new">Plan a trip <ArrowUpRight aria-hidden="true" className="size-4" /></Link>
          <button aria-expanded={isMenuOpen} aria-label={isMenuOpen ? 'Close navigation menu' : 'Open navigation menu'} className="menu-toggle" type="button" onClick={() => setIsMenuOpen((open) => !open)}>{isMenuOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}</button>
        </div>
        {isMenuOpen && <motion.nav animate={{ opacity: 1, y: 0 }} className="mobile-nav" initial={{ opacity: 0, y: -8 }} aria-label="Mobile navigation"><a href="#product" onClick={closeMenu}>Product</a><a href="#how-it-works" onClick={closeMenu}>How it works</a><a href="#groups" onClick={closeMenu}>For groups</a>{user ? <><Link to="/home" onClick={closeMenu}>My trips</Link><button className="mobile-auth-button" type="button" onClick={() => { logout(); closeMenu() }}>Sign out</button></> : <Link to="/auth?mode=login" onClick={closeMenu}>Sign in</Link>}<Link to="/trips/new" onClick={closeMenu}>Plan a trip</Link></motion.nav>}
      </header>

      <main id="top">
        <section className="hero-section shell" aria-labelledby="hero-title">
          <motion.div animate="visible" className="hero-copy" initial="hidden" transition={{ duration: 0.52, ease: [0.16, 1, 0.3, 1] }} variants={fadeUp}>
            <p className="eyebrow"><Compass aria-hidden="true" /> Group travel, made clear</p>
            <h1 id="hero-title" className="display-title">Turn scattered ideas into one shared trip plan.</h1>
            <p className="hero-description">Wandora brings everyone&apos;s places, preferences, budgets, and notes into one calm workspace your whole group can follow.</p>
            <div className="hero-actions"><Link className="button button-primary" to="/trips/new">Start planning <ArrowRight aria-hidden="true" className="size-4" /></Link><a className="button button-secondary" href="#how-it-works">See how it works</a></div>
            <p className="hero-note"><span className="avatar-stack" aria-hidden="true"><span /> <span /> <span /></span>For friends, families, and the people who never agree on dinner.</p>
          </motion.div>
          <JourneyPreview />
        </section>

        <motion.section className="feature-band shell" id="product" initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={fadeUp}>
          <FeatureBandItem icon={<UsersRound />} title="Plan together" text="Votes and comments stay attached to each place." />
          <FeatureBandItem icon={<MapPinned />} title="Route smarter" text="Time, weather, and distance stay in the conversation." />
          <FeatureBandItem icon={<ListChecks />} title="Pack clearly" text="One shared checklist keeps the last-minute scramble small." />
          <FeatureBandItem icon={<WalletCards />} title="Spend calmly" text="Budgets update before the group makes a decision." />
        </motion.section>

        <section className="section shell" id="how-it-works" aria-labelledby="workflow-title">
          <motion.div className="section-heading" initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={fadeUp}><p className="eyebrow">A better way to begin</p><h2 id="workflow-title" className="section-title">From group chat to a trip everyone can follow.</h2><p className="section-description">Wandora gives the messy middle of planning a place to settle.</p></motion.div>
          <div className="workflow-grid"><WorkflowStep step="01" icon={<CalendarDays />} title="Collect the trip" text="Add dates, a destination, a budget, and the preferences that make this group yours." /><WorkflowStep step="02" icon={<Compass />} title="Shape the route" text="Wandora turns the group&apos;s input into a first itinerary with clear choices to review." /><WorkflowStep step="03" icon={<Clock3 />} title="Keep it moving" text="Adjust the plan as people vote, places change, and the trip gets closer." /></div>
        </section>

        <motion.section className="product-proof shell" id="groups" initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.15 }} variants={fadeUp}>
          <div className="proof-image-wrap"><img src="/planning-board-preview.png" alt="Wandora planning board showing a route, group decisions, and trip preparation progress" /></div>
          <div className="proof-copy"><p className="eyebrow">One workspace, many opinions</p><h2 className="section-title">The itinerary is not a static list.</h2><p className="section-description">It is the shared memory of the trip taking shape: saved places, open decisions, a route to refine, and preparation that stays visible.</p><div className="proof-list"><ProofItem text="Everyone sees what is decided and what still needs a vote." /><ProofItem text="AI suggestions stay short, useful, and easy to edit." /><ProofItem text="Budget, packing, and day notes live beside the route." /></div><Link className="text-link" to="/trips/new">Make a shared plan <ChevronRight aria-hidden="true" className="size-4" /></Link></div>
        </motion.section>

        <section className="section shell" id="start" aria-labelledby="start-title"><motion.div className="start-panel" initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.25 }} variants={fadeUp}><div className="start-copy"><p className="eyebrow">Start with one destination</p><h2 id="start-title" className="section-title">Bring the first idea. We&apos;ll help shape the rest.</h2><p className="section-description">Join the early access list and be part of building a calmer way to plan trips together.</p></div><WaitlistForm /></motion.div></section>
      </main>

      <footer className="site-footer shell"><a className="wordmark" href="#top">Wandora</a><p>Group travel planning with a little more room to think.</p><p className="footer-meta">© 2026 Wandora · Built for better shared journeys</p></footer>
    </div>
  )
}

function JourneyPreview() {
  return <motion.div animate={{ opacity: 1, scale: 1 }} className="journey-visual" initial={{ opacity: 0, scale: 0.97 }} transition={{ delay: 0.12, duration: 0.62, ease: [0.16, 1, 0.3, 1] }} aria-label="A preview of a shared Wandora trip plan" role="img"><div className="visual-topline"><div><p className="visual-kicker">Shared workspace</p><p className="visual-title">Da Nang, Hoi An &amp; Hue</p></div><div className="visual-meta"><UsersRound aria-hidden="true" /> 6 travelers</div></div><div className="map-board"><div className="map-label map-label-one">My Khe beach</div><div className="map-label map-label-two">Old town</div><div className="map-label map-label-three">Lantern walk</div><div className="route-segment route-segment-one" /><div className="route-segment route-segment-two" /><div className="route-segment route-segment-three" /><div className="waypoint waypoint-one"><span /></div><div className="waypoint waypoint-two"><span /></div><div className="waypoint waypoint-three"><span /></div><div className="waypoint waypoint-four"><span /></div><div className="map-legend"><span className="legend-dot" /> Route draft <span className="legend-dot legend-dot-sand" /> Group vote</div></div><motion.div animate={{ opacity: 1, y: 0 }} className="suggestion-note" initial={{ opacity: 0, y: 10 }} transition={{ delay: 0.55, duration: 0.4 }}><div className="suggestion-icon"><MapPinned aria-hidden="true" /></div><div><p className="suggestion-label">Wandora suggests</p><p>Move the beach stop earlier for cooler light.</p></div><Check aria-hidden="true" className="suggestion-check" /></motion.div><div className="itinerary-card"><div className="itinerary-header"><span>Day 2</span><span className="status-pill">Draft</span></div><div className="itinerary-row"><span className="time">09:30</span><span className="timeline-dot sand-dot" /><span>Market breakfast</span></div><div className="itinerary-row"><span className="time">11:00</span><span className="timeline-dot" /><span>Basket boat village</span></div><div className="itinerary-row"><span className="time">17:00</span><span className="timeline-dot" /><span>Lantern walk</span></div></div></motion.div>
}

function FeatureBandItem({ icon, title, text }: { icon: ReactNode; title: string; text: string }) {
  return <div className="feature-item"><div className="feature-icon" aria-hidden="true">{icon}</div><div><h3>{title}</h3><p>{text}</p></div></div>
}

function WorkflowStep({ step, icon, title, text }: { step: string; icon: ReactNode; title: string; text: string }) {
  return <motion.article className="workflow-step" initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} transition={{ duration: 0.36 }} viewport={{ once: true, amount: 0.2 }}><div className="step-topline"><span>{step}</span><span className="step-icon" aria-hidden="true">{icon}</span></div><h3>{title}</h3><p>{text}</p></motion.article>
}

function ProofItem({ text }: { text: string }) {
  return <p className="proof-item"><Check aria-hidden="true" /> {text}</p>
}

function WaitlistForm() {
  const [submittedName, setSubmittedName] = useState('')
  const { register, handleSubmit, formState: { errors, isSubmitSuccessful } } = useForm<WaitlistValues>({ resolver: zodResolver(waitlistSchema), defaultValues: { name: '', email: '' } })
  return <form className="waitlist-form" onSubmit={handleSubmit((values) => setSubmittedName(values.name))}><div className="form-row"><div className="form-field"><Label htmlFor="waitlist-name">Your name</Label><Input id="waitlist-name" placeholder="Le Thanh" {...register('name')} />{errors.name && <p className="form-error">{errors.name.message}</p>}</div><div className="form-field"><Label htmlFor="waitlist-email">Email address</Label><Input id="waitlist-email" type="email" placeholder="you@example.com" {...register('email')} />{errors.email && <p className="form-error">{errors.email.message}</p>}</div></div><Button className="form-submit" type="submit">Join early access <ArrowRight aria-hidden="true" className="size-4" /></Button>{isSubmitSuccessful && <p className="form-success" role="status"><Check aria-hidden="true" /> Thanks, {submittedName}. We&apos;ll keep you posted.</p>}</form>
}
