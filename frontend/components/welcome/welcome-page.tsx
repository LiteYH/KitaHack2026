'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Sparkles, TrendingUp, Zap } from 'lucide-react'

export function WelcomePage() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-200/40 via-transparent to-transparent animate-pulse" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_var(--tw-gradient-stops))] from-purple-200/40 via-transparent to-transparent animate-pulse" />
      
      {/* Floating light effects */}
      <div className="absolute left-1/4 top-1/4 h-96 w-96 animate-pulse rounded-full bg-blue-400/20 blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 h-96 w-96 animate-pulse rounded-full bg-purple-400/20 blur-3xl" style={{ animationDelay: '1s' }} />
      <div className="absolute top-1/2 right-1/3 h-80 w-80 animate-pulse rounded-full bg-indigo-400/15 blur-3xl" style={{ animationDelay: '2s' }} />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center space-y-8 px-4 text-center">
        {/* Header with logo */}
        <header className="absolute left-0 right-0 top-0 flex items-center justify-between p-6 md:p-8">
          <div className="flex items-center space-x-3 animate-fade-in">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">BossolutionAI</span>
          </div>
          <nav className="flex items-center space-x-6 animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <Link 
              href="/chat" 
              className="text-sm font-medium text-slate-700 transition-colors hover:text-blue-600"
            >
              Home
            </Link>
            <Link 
              href="/docs" 
              className="text-sm font-medium text-slate-700 transition-colors hover:text-purple-600"
            >
              Docs
            </Link>
          </nav>
        </header>

        {/* Main content */}
        <div className="mt-32 flex flex-col items-center space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 rounded-full border border-blue-300/50 bg-white/70 px-4 py-2 backdrop-blur-sm animate-slide-down shadow-sm">
            <Zap className="h-4 w-4 text-blue-600 animate-pulse" />
            <span className="text-sm font-medium bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">AI-Powered Marketing</span>
          </div>

          {/* Heading */}
          <h1 className="max-w-4xl text-5xl font-bold leading-tight tracking-tight text-slate-900 md:text-6xl lg:text-7xl">
            <span className="inline-block animate-slide-up">
              Empower your business
            </span>
            <br />
            <span className="inline-block animate-slide-up bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent" style={{ animationDelay: '0.2s' }}>
              with AI-driven marketing
            </span>
          </h1>

          {/* Subtitle */}
          <p className="max-w-2xl text-lg text-slate-600 animate-fade-in md:text-xl" style={{ animationDelay: '0.4s' }}>
            Automate content creation, analyze competitors, optimize campaigns, and boost your ROI — all powered by AI.
          </p>

          {/* Buttons */}
          <div className="flex flex-col items-center space-y-4 pt-8 sm:flex-row sm:space-x-4 sm:space-y-0 animate-fade-in" style={{ animationDelay: '0.6s' }}>
            <Link href="/chat">
              <Button 
                size="lg" 
                className="rounded-full bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-6 text-base font-semibold text-white shadow-lg transition-all hover:scale-105 hover:shadow-2xl hover:from-blue-700 hover:to-purple-700"
              >
                Get Started
                <Sparkles className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Button 
              size="lg" 
              variant="outline" 
              className="rounded-full border-2 border-slate-300 bg-white/70 px-8 py-6 text-base font-semibold text-slate-800 backdrop-blur-sm transition-all hover:bg-white hover:scale-105 hover:border-blue-400"
            >
              Learn More
            </Button>
          </div>

          {/* Feature highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 max-w-4xl animate-fade-in" style={{ animationDelay: '0.8s' }}>
            <div className="flex flex-col items-center space-y-2 p-4 rounded-xl bg-white/50 backdrop-blur-sm border border-blue-200/50 transition-all hover:scale-105 hover:bg-white/70">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                <Sparkles className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-slate-900">AI Content Creation</h3>
              <p className="text-xs text-slate-600 text-center">Generate engaging content in seconds</p>
            </div>
            <div className="flex flex-col items-center space-y-2 p-4 rounded-xl bg-white/50 backdrop-blur-sm border border-purple-200/50 transition-all hover:scale-105 hover:bg-white/70">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-100">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-slate-900">Smart Analytics</h3>
              <p className="text-xs text-slate-600 text-center">Track ROI and optimize campaigns</p>
            </div>
            <div className="flex flex-col items-center space-y-2 p-4 rounded-xl bg-white/50 backdrop-blur-sm border border-indigo-200/50 transition-all hover:scale-105 hover:bg-white/70">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100">
                <Zap className="h-6 w-6 text-indigo-600" />
              </div>
              <h3 className="font-semibold text-slate-900">Auto Publishing</h3>
              <p className="text-xs text-slate-600 text-center">Schedule posts across all platforms</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-50 to-transparent" />
    </div>
  )
}
