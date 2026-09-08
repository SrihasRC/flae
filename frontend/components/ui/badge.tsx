import { mergeProps } from "@base-ui/react/merge-props"
import { useRender } from "@base-ui/react/use-render"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "cn"

const badgeVariants = cva(
  "group/badge inline-flex h-5 w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-4xl border border-transparent px-2 py-0.5 text-xs font-medium whitespace-nowrap transition-all focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&>svg]:pointer-events-none [&>svg]:size-3!",
  {
    variants: {
      variant: {
        default: "bg-coral text-white",
        secondary:
          "bg-surface-soft text-ink border border-hairline",
        destructive:
          "bg-destructive/15 text-destructive border border-destructive/30",
        outline:
          "border-hairline text-ink bg-canvas",
        ghost:
          "hover:bg-surface-card hover:text-ink",
        link: "text-coral underline-offset-4 hover:underline",
        pill: "bg-surface-card text-ink border border-hairline",
        coral: "bg-coral text-white",
        dark: "bg-surface-dark text-canvas border border-surface-dark-elevated",
        teal: "bg-accent-teal/15 text-teal-800 dark:text-teal-300 border border-accent-teal/30",
        amber: "bg-accent-amber/15 text-amber-800 dark:text-amber-300 border border-accent-amber/30",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant = "default",
  render,
  ...props
}: useRender.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return useRender({
    defaultTagName: "span",
    props: mergeProps<"span">(
      {
        className: cn(badgeVariants({ variant }), className),
      },
      props
    ),
    render,
    state: {
      slot: "badge",
      variant,
    },
  })
}

export { Badge, badgeVariants }
