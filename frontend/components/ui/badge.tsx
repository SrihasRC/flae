import { mergeProps } from "@base-ui/react/merge-props"
import { useRender } from "@base-ui/react/use-render"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "cn"

const badgeVariants = cva(
  "group/badge inline-flex h-5 w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-4xl border border-transparent px-2 py-0.5 text-xs font-medium whitespace-nowrap transition-all focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&>svg]:pointer-events-none [&>svg]:size-3!",
  {
    variants: {
      variant: {
        default: "bg-[#cc785c] text-white",
        secondary:
          "bg-[#f5f0e8] text-[#141413] border border-[#e6dfd8]",
        destructive:
          "bg-[#c64545]/15 text-[#c64545] border border-[#c64545]/30",
        outline:
          "border-[#e6dfd8] text-[#141413] bg-[#faf9f5]",
        ghost:
          "hover:bg-[#efe9de] hover:text-[#141413]",
        link: "text-[#cc785c] underline-offset-4 hover:underline",
        pill: "bg-[#efe9de] text-[#141413] border border-[#e6dfd8]",
        coral: "bg-[#cc785c] text-white",
        dark: "bg-[#181715] text-[#faf9f5] border border-[#252320]",
        teal: "bg-[#5db8a6]/15 text-[#2b7264] border border-[#5db8a6]/30",
        amber: "bg-[#e8a55a]/15 text-[#9e5f1b] border border-[#e8a55a]/30",
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
