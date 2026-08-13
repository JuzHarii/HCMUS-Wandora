import type { ReactNode } from 'react'

type FormFieldProps = {
  label: string
  error?: string
  className?: string
  children: ReactNode
}

export function FormField({ label, error, className = '', children }: FormFieldProps) {
  return <label className={`trip-field ${className}`}><span>{label}</span>{children}{error && <small data-testid="trip-validation-alert">{error}</small>}</label>
}
