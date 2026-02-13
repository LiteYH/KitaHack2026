export function UiGraphLogo({ className = "h-20 w-20" }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 120" fill="none" className={className}>
      <circle cx="60" cy="60" r="60" fill="hsl(217 91% 96%)" />
      <path
        d="M40 42C40 38.6863 42.6863 36 46 36H60C70.4934 36 79 44.5066 79 55C79 65.4934 70.4934 74 60 74H52V84C52 85.1046 51.1046 86 50 86H46C44.8954 86 44 85.1046 44 84V46H40V42Z"
        fill="hsl(217 91% 55%)"
      />
      <path
        d="M52 62H60C63.866 62 67 58.866 67 55C67 51.134 63.866 48 60 48H52V62Z"
        fill="hsl(217 91% 96%)"
      />
      <path
        d="M60 55C60 51.134 63.134 48 67 48H72C75.866 48 79 51.134 79 55V55C79 58.866 75.866 62 72 62H60V55Z"
        fill="hsl(217 91% 45%)"
      />
    </svg>
  )
}
