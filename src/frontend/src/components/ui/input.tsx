import type { ComponentProps } from 'react'

import { cn } from '@/lib/utils'

function Input({ className, type, ...props }: ComponentProps<'input'>) {
  return (
    <input
      type={type}
      className={cn(
        'flex h-10 w-full rounded-md border border-[#c9d8d0] bg-white px-3 py-2 text-sm text-[#172426] outline-none transition-colors placeholder:text-[#7a8c8f] focus:border-[#2f6f73] focus:ring-2 focus:ring-[#2f6f73]/20 disabled:cursor-not-allowed disabled:opacity-50',
        className,
      )}
      {...props}
    />
  )
}

export { Input }
