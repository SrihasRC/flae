import { Button as ButtonPrimitive } from "@base-ui/react/button"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "cn"

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-lg border border-transparent bg-clip-padding text-sm font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-[#cc785c] text-white hover:bg-[#a9583e] active:bg-[#a9583e]",
        outline:
          "border-[#e6dfd8] bg-[#faf9f5] text-[#141413] hover:bg-[#f5f0e8] hover:text-[#141413] dark:border-[#2e2b27] dark:bg-[#181715] dark:text-[#faf9f5] dark:hover:bg-[#252320]",
        secondary:
          "bg-[#faf9f5] text-[#141413] border border-[#e6dfd8] hover:bg-[#f5f0e8] active:bg-[#efe9de]",
        ghost:
          "hover:bg-[#efe9de] hover:text-[#141413] dark:hover:bg-[#252320] dark:hover:text-[#faf9f5]",
        destructive:
          "bg-[#c64545]/15 text-[#c64545] hover:bg-[#c64545]/25 focus-visible:border-[#c64545]/40",
        link: "text-[#cc785c] underline-offset-4 hover:underline",
        coral: "bg-[#cc785c] text-white hover:bg-[#a9583e] active:bg-[#a9583e]",
        cream: "bg-[#efe9de] text-[#141413] border border-[#e6dfd8] hover:bg-[#e8e0d2]",
        "secondary-on-dark": "bg-[#252320] text-[#faf9f5] border border-[#383530] hover:bg-[#2e2b27]",
      },
      size: {
        default:
          "h-8 gap-1.5 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
        xs: "h-6 gap-1 rounded-[min(var(--radius-md),10px)] px-2 text-xs in-data-[slot=button-group]:rounded-lg has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-7 gap-1 rounded-[min(var(--radius-md),12px)] px-2.5 text-[0.8rem] in-data-[slot=button-group]:rounded-lg has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3.5",
        lg: "h-9 gap-1.5 px-2.5 has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2",
        icon: "size-8",
        "icon-xs":
          "size-6 rounded-[min(var(--radius-md),10px)] in-data-[slot=button-group]:rounded-lg [&_svg:not([class*='size-'])]:size-3",
        "icon-sm":
          "size-7 rounded-[min(var(--radius-md),12px)] in-data-[slot=button-group]:rounded-lg",
        "icon-lg": "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
