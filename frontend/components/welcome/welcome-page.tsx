'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Sparkles } from 'lucide-react'

export function WelcomePage() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-100/40 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-indigo-100/40 via-transparent to-transparent" />
      
      {/* Floating light effects */}
      <div className="absolute left-1/4 top-1/4 h-96 w-96 animate-pulse rounded-full bg-blue-300/20 blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 h-96 w-96 animate-pulse rounded-full bg-indigo-300/20 blur-3xl delay-1000" />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center space-y-8 px-4 text-center">
        {/* Header with logo */}
        <header className="absolute left-0 right-0 top-0 flex items-center justify-between p-6 md:p-8">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-800">React Bits</span>
          </div>
          <nav className="flex items-center space-x-6">
            <Link 
              href="/chat" 
              className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-900"
            >
              Home
            </Link>
            <Link 
              href="/docs" 
              className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-900"
            >
              Docs
            </Link>
          </nav>
        </header>

        {/* Main content */}
        <div className="mt-32 flex flex-col items-center space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 rounded-full border border-slate-300 bg-white/60 px-4 py-2 backdrop-blur-sm">
            <Sparkles className="h-4 w-4 text-indigo-600" />
            <span className="text-sm font-medium text-slate-700">New Background</span>
          </div>

          {/* Heading */}
          <h1 className="max-w-4xl text-5xl font-bold leading-tight tracking-tight text-slate-800 md:text-6xl lg:text-7xl">
            May these lights guide
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              you on your path
            </span>
          </h1>

          {/* Buttons */}
          <div className="flex flex-col items-center space-y-4 pt-8 sm:flex-row sm:space-x-4 sm:space-y-0">
            <Link href="/chat">
              <Button 
                size="lg" 
                className="rounded-full bg-gradient-to-r from-slate-200 to-slate-300 px-8 py-6 text-base font-semibold text-slate-800 shadow-lg transition-all hover:scale-105 hover:shadow-xl"
              >
                Get Started
              </Button>
            </Link>
            <Button 
              size="lg" 
              variant="outline" 
              className="rounded-full border-2 border-slate-300 bg-transparent px-8 py-6 text-base font-semibold text-slate-700 backdrop-blur-sm transition-all hover:bg-white/50 hover:scale-105"
            >
              Learn More
            </Button>
          </div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-50 to-transparent" />
    </div>
  )
}
