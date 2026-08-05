import { cva } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md text-sm font-semibold transition-colors outline-none focus-visible:ring-2 focus-visible:ring-[#2f6f73] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-[#172426] text-white hover:bg-[#2b3d40]',
        outline:
          'border border-[#c9d8d0] bg-white text-[#172426] hover:bg-[#eef4ef]',
        ghost: 'text-[#172426] hover:bg-[#eef4ef]',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 px-3',
        lg: 'h-11 px-6',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export { buttonVariants }
