import type { ComponentProps } from 'react'

import { cn } from '@/lib/utils'

function Label({ className, ...props }: ComponentProps<'label'>) {
  return (
    <label
      className={cn('text-sm font-semibold leading-none text-[#172426]', className)}
      {...props}
    />
  )
}

export { Label }
