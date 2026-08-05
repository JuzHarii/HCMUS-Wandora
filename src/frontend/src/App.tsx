import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight, CircleCheck, Component, Route, Sparkles } from 'lucide-react'
import { motion } from 'motion/react'
import { type ReactNode, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, NavLink, Route as RouterRoute, Routes } from 'react-router'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { buttonVariants } from '@/components/ui/button-variants'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'

const waitlistSchema = z.object({
  name: z.string().min(2, 'Use at least 2 characters.'),
  email: z.string().email('Enter a valid email address.'),
  role: z.string().min(2, 'Tell us what you are building.'),
})

type WaitlistValues = z.infer<typeof waitlistSchema>

function App() {
  return (
    <div className="min-h-screen bg-[#f6f8f3] text-[#172426]">
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-5 py-5">
        <NavLink to="/" className="flex items-center gap-2 font-bold">
          <span className="grid size-9 place-items-center rounded-md bg-[#172426] text-white">
            W
          </span>
          Wandora
        </NavLink>
        <nav className="flex items-center gap-1 rounded-md border border-[#d6e1da] bg-white p-1">
          <NavItem to="/">Home</NavItem>
          <NavItem to="/stack">Stack</NavItem>
        </nav>
      </header>

      <Routes>
        <RouterRoute path="/" element={<HomePage />} />
        <RouterRoute path="/stack" element={<StackPage />} />
      </Routes>
    </div>
  )
}

function NavItem({ to, children }: { to: string; children: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(
          'rounded px-3 py-2 text-sm font-semibold transition-colors',
          isActive
            ? 'bg-[#172426] text-white'
            : 'text-[#516164] hover:bg-[#eef4ef] hover:text-[#172426]',
        )
      }
    >
      {children}
    </NavLink>
  )
}

function HomePage() {
  const [submittedName, setSubmittedName] = useState('')
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitSuccessful },
  } = useForm<WaitlistValues>({
    resolver: zodResolver(waitlistSchema),
    defaultValues: {
      name: '',
      email: '',
      role: '',
    },
  })

  function onSubmit(values: WaitlistValues) {
    setSubmittedName(values.name)
  }

  return (
    <main className="mx-auto grid w-full max-w-6xl gap-8 px-5 pb-12 pt-8 md:grid-cols-[1.1fr_0.9fr] md:items-center">
      <motion.section
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: 'easeOut' }}
        className="space-y-6"
      >
        <p className="inline-flex items-center gap-2 rounded-md border border-[#c9d8d0] bg-white px-3 py-2 text-sm font-semibold text-[#2f6f73]">
          <Sparkles className="size-4" />
          Modern React stack installed
        </p>
        <div className="space-y-4">
          <h1 className="max-w-3xl text-5xl font-bold leading-[1.02] md:text-7xl">
            A sharper frontend base for Wandora.
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-[#58676a]">
            Tailwind CSS, shadcn/ui patterns, React Router, React Hook Form,
            Zod, and Motion for React are wired together and ready for product
            work.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link to="/stack" className={buttonVariants({ variant: 'default' })}>
            Start building
            <ArrowRight className="size-4" />
          </Link>
          <Link to="/stack" className={buttonVariants({ variant: 'outline' })}>
            View stack
          </Link>
        </div>
      </motion.section>

      <section className="rounded-md border border-[#d6e1da] bg-white p-5 shadow-sm">
        <div className="mb-5">
          <h2 className="text-xl font-bold">Validated signup</h2>
          <p className="mt-1 text-sm text-[#58676a]">
            React Hook Form plus Zod resolver, styled with shadcn/ui primitives.
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <FieldError message={errors.name?.message}>
            <Label htmlFor="name">Name</Label>
            <Input id="name" placeholder="Le Thanh" {...register('name')} />
          </FieldError>

          <FieldError message={errors.email?.message}>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              {...register('email')}
            />
          </FieldError>

          <FieldError message={errors.role?.message}>
            <Label htmlFor="role">What are you building?</Label>
            <Input id="role" placeholder="Trip planner, marketplace..." {...register('role')} />
          </FieldError>

          <Button className="w-full" type="submit">
            Join waitlist
          </Button>
        </form>

        {isSubmitSuccessful && (
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 flex items-center gap-2 rounded-md bg-[#eef7ed] px-3 py-2 text-sm font-semibold text-[#2f6f3c]"
          >
            <CircleCheck className="size-4" />
            {submittedName}, your form passed validation.
          </motion.p>
        )}
      </section>
    </main>
  )
}

function FieldError({
  children,
  message,
}: {
  children: ReactNode
  message?: string
}) {
  return (
    <div className="space-y-2">
      {children}
      {message && <p className="text-sm font-medium text-[#b42318]">{message}</p>}
    </div>
  )
}

function StackPage() {
  const stackItems = [
    ['Tailwind CSS', 'Utility styling through the official Vite plugin.', Sparkles],
    ['shadcn/ui', 'Local component primitives with variants and cn().', Component],
    ['React Router', 'Client routing with BrowserRouter and route views.', Route],
    ['React Hook Form', 'Fast, typed form state without noisy re-renders.', CircleCheck],
    ['Zod', 'Runtime validation and inferred form types.', CircleCheck],
    ['Motion for React', 'Declarative entrance and feedback animations.', Sparkles],
  ] as const

  return (
    <main className="mx-auto w-full max-w-6xl px-5 pb-12 pt-8">
      <div className="mb-8 max-w-2xl">
        <h1 className="text-4xl font-bold">Frontend stack</h1>
        <p className="mt-3 text-[#58676a]">
          These pieces are installed, imported, and represented in working app
          code so future screens can build from them directly.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {stackItems.map(([name, description, Icon]) => (
          <article
            key={name}
            className="rounded-md border border-[#d6e1da] bg-white p-5 shadow-sm"
          >
            <Icon className="mb-5 size-5 text-[#2f6f73]" />
            <h2 className="text-lg font-bold">{name}</h2>
            <p className="mt-2 text-sm leading-6 text-[#58676a]">{description}</p>
          </article>
        ))}
      </div>
    </main>
  )
}

export default App
