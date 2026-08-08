'use client';

import { ShieldCheck, AlertTriangle, Languages, MicOff, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
  micPermissionBlocked?: boolean;
  onRequestMicPermission?: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  micPermissionBlocked = false,
  onRequestMicPermission,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="w-full max-w-4xl mx-auto px-4 py-8 flex flex-col items-center justify-center min-h-svh">
      {/* Dhan Rakshak Brand & Avatar */}
      <section className="flex flex-col items-center text-center mb-8">
        <div className="relative mb-6 group">
          <div className="absolute -inset-1.5 bg-gradient-to-r from-blue-600 to-amber-500 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-1000 group-hover:duration-200 animate-pulse"></div>
          <img
            src="/avatar.png"
            alt="Dhan Rakshak Guardian Avatar"
            className="relative rounded-full size-32 object-cover border-4 border-background shadow-2xl transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full border-2 border-background shadow-lg">
            <ShieldCheck className="size-5" />
          </div>
        </div>

        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-600 via-indigo-500 to-amber-500 bg-clip-text text-transparent mb-2">
          धन रक्षक (Dhan Rakshak)
        </h1>
        <p className="text-muted-foreground text-lg max-w-lg font-medium">
          Your AI Financial Services Voice Assistant for Secure &amp; Smart Banking
        </p>
      </section>

      {/* Safety & Info Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl mb-8">
        <div className="bg-card border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col items-start">
          <div className="bg-blue-500/10 text-blue-600 dark:text-blue-400 p-3 rounded-xl mb-4">
            <ShieldCheck className="size-6" />
          </div>
          <h3 className="font-bold text-foreground mb-2">100% Secure</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Dhan Rakshak will <strong>NEVER</strong> ask for your OTP, ATM PIN, UPI PIN, CVV, or full bank account details.
          </p>
        </div>

        <div className="bg-card border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col items-start">
          <div className="bg-amber-500/10 text-amber-600 dark:text-amber-400 p-3 rounded-xl mb-4">
            <AlertTriangle className="size-6" />
          </div>
          <h3 className="font-bold text-foreground mb-2">Scam Awareness</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            No police, RBI, or government agency will place you under <strong>"digital arrest"</strong> over phone or video calls.
          </p>
        </div>

        <div className="bg-card border rounded-2xl p-5 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col items-start">
          <div className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 p-3 rounded-xl mb-4">
            <Languages className="size-6" />
          </div>
          <h3 className="font-bold text-foreground mb-2">Multi-Lingual</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Dhan Rakshak understands and speaks <strong>Hindi, English, and Hinglish</strong> to support everyone.
          </p>
        </div>
      </section>

      {/* Connection & Microphone Permission Error Handling */}
      <section className="w-full max-w-md flex flex-col items-center gap-4">
        {micPermissionBlocked ? (
          <div className="w-full bg-destructive/10 border border-destructive/20 rounded-2xl p-5 text-center flex flex-col items-center">
            <div className="bg-destructive/20 text-destructive p-3 rounded-full mb-3">
              <MicOff className="size-8" />
            </div>
            <h4 className="font-bold text-destructive mb-2">Microphone Access Blocked</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Dhan Rakshak requires your microphone to listen to your banking questions.
            </p>
            <div className="bg-background border rounded-xl p-3 text-left w-full text-xs text-muted-foreground space-y-2 mb-4">
              <p className="font-semibold text-foreground flex items-center gap-1">
                <Info className="size-3.5 text-blue-500" /> How to enable:
              </p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Click the <strong>Lock 🔒 or Camera/Microphone icon</strong> in your browser's address bar.</li>
                <li>Toggle the <strong>Microphone</strong> permission to <strong>Allow</strong>.</li>
                <li>Refresh the page to apply changes.</li>
              </ol>
            </div>
            <Button
              onClick={onRequestMicPermission}
              className="w-full rounded-xl font-bold bg-destructive hover:bg-destructive/95 text-white"
            >
              Try Enabling Again
            </Button>
          </div>
        ) : (
          <div className="w-full flex flex-col items-center">
            <Button
              size="lg"
              onClick={onStartCall}
              className="w-64 rounded-full font-bold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xl shadow-blue-500/20 hover:scale-105 active:scale-95 transition-all duration-200 text-sm tracking-wider uppercase h-12"
            >
              {startButtonText}
            </Button>
            <p className="text-xs text-muted-foreground mt-4 text-center">
              Click to start call. Make sure your microphone is enabled.
            </p>
          </div>
        )}
      </section>
    </div>
  );
};
