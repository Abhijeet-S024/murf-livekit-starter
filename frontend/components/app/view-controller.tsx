'use client';

import { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';
import { Track } from 'livekit-client';
import {
  AlertTriangle,
  Award,
  Ban,
  Coins,
  CreditCard,
  Eye,
  Globe,
  GraduationCap,
  HelpCircle,
  Info,
  KeyRound,
  Landmark,
  Loader2,
  Lock,
  Mic,
  MicOff,
  PhoneOff,
  RefreshCw,
  Shield,
  ShieldCheck,
} from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import {
  useSessionContext,
  useSessionMessages,
  useTrackToggle,
  useVoiceAssistant,
} from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentChatTranscript } from '@/components/agents-ui/agent-chat-transcript';
import { AudioVisualizer } from '@/components/agents-ui/blocks/agent-session-view-01/components/audio-visualizer';
import { Button } from '@/components/ui/button';

interface ViewControllerProps {
  appConfig: AppConfig;
}

export function ViewController({ appConfig }: ViewControllerProps) {
  const session = useSessionContext();
  const { isConnected, start, end, connectionState } = session;
  const { resolvedTheme } = useTheme();

  // Get active assistant state
  const { state: agentState } = useVoiceAssistant();

  // Get chat messages from session data stream
  const { messages, send } = useSessionMessages(session);

  const [chatText, setChatText] = useState('');
  const [micPermissionBlocked, setMicPermissionBlocked] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [hasConnectedOnce, setHasConnectedOnce] = useState(false);
  const [callEnded, setCallEnded] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<'hindi' | 'english' | 'hinglish'>(
    'hindi'
  );

  // Mic toggle for active session
  const microphoneToggle = useTrackToggle({
    source: Track.Source.Microphone,
  });

  // Track connection states
  useEffect(() => {
    if (isConnected) {
      setIsConnecting(false);
      setHasConnectedOnce(true);
      setCallEnded(false);
    }
  }, [isConnected]);

  useEffect(() => {
    if (connectionState === 'disconnected' && hasConnectedOnce) {
      setCallEnded(true);
    }
  }, [connectionState, hasConnectedOnce]);

  const requestMicPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
      setMicPermissionBlocked(false);
      return true;
    } catch (err: unknown) {
      const domErr = err as { name?: string };
      if (domErr.name === 'NotAllowedError' || domErr.name === 'PermissionDeniedError') {
        setMicPermissionBlocked(true);
      }
      return false;
    }
  };

  const handleStartCall = async () => {
    const micGranted = await requestMicPermission();
    if (!micGranted) return;

    try {
      setIsConnecting(true);
      setCallEnded(false);
      await start();
    } catch (err) {
      console.error('Failed to start call:', err);
      setIsConnecting(false);
    }
  };

  const handleRestartCall = async () => {
    setCallEnded(false);
    setHasConnectedOnce(false);
    handleStartCall();
  };

  // Start or end call based on click
  const handleCenterpieceClick = () => {
    if (isConnected) {
      end();
    } else {
      handleStartCall();
    }
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-hidden bg-[#F5F8FC] font-sans text-[#172033] selection:bg-[#F28C28]/20 selection:text-[#12355B]">
      {/* Background pattern */}
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,#e5effa_1px,transparent_1px),linear-gradient(to_bottom,#e5effa_1px,transparent_1px)] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] bg-[size:4rem_4rem] opacity-60" />

      {/* HEADER */}
      <header className="sticky top-0 z-40 w-full border-b border-[#D9E1EC] bg-white/80 backdrop-blur-md transition-all">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="rounded-xl border-2 border-white bg-[#12355B] p-2 text-white shadow-md">
              <svg
                className="size-6 text-[#F28C28]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2.5"
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-lg font-bold text-[#12355B]">धन रक्षक</span>
                <span className="text-xs font-semibold text-[#5B667A]">Dhan Rakshak</span>
              </div>
              <div className="hidden rounded-full border border-[#1769AA]/20 bg-[#1769AA]/10 px-2 py-0.5 text-[10px] font-bold tracking-wider text-[#1769AA] uppercase sm:inline-block">
                Secure AI Financial Assistant
              </div>
            </div>
          </div>
          <nav className="hidden items-center gap-6 text-sm font-semibold text-[#5B667A] md:flex">
            <a href="#safety" className="transition-colors hover:text-[#12355B]">
              Banking Safety
            </a>
            <a href="#digital" className="transition-colors hover:text-[#12355B]">
              Digital Payments
            </a>
            <a href="#schemes" className="transition-colors hover:text-[#12355B]">
              Financial Schemes
            </a>
            <a href="#help" className="transition-colors hover:text-[#12355B]">
              Help
            </a>
            <a
              href="http://localhost:5050/analytics"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 rounded-lg bg-[#1769AA] px-3 py-1.5 text-xs font-bold text-white shadow-sm transition-colors hover:bg-[#12355B]"
            >
              <svg className="size-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              Analytics
            </a>
          </nav>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="relative mx-auto w-full max-w-7xl px-4 pt-12 pb-6 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-12 lg:flex-row">
          <div className="max-w-xl text-center lg:text-left">
            <span className="mb-4 inline-flex items-center gap-1.5 rounded-full border border-[#F28C28]/20 bg-[#F28C28]/10 px-3 py-1 text-xs font-bold text-[#F28C28]">
              <Award className="size-3.5" /> सुरक्षित बैंकिंग, सरल मार्गदर्शन
            </span>
            <h1 className="mb-4 text-4xl leading-[1.1] font-extrabold tracking-tight text-[#12355B] md:text-5xl lg:text-6xl">
              Your Trusted Guide to <span className="text-[#1769AA]">Safe Banking</span>
            </h1>
            <p className="mb-6 text-base font-medium text-[#5B667A] md:text-lg">
              Understand banking, digital payments and financial services through a simple voice
              conversation.
            </p>
            <div className="mx-auto flex w-fit items-center justify-center gap-2 rounded-xl border border-[#1769AA]/10 bg-[#1769AA]/5 px-4 py-2 text-xs font-bold text-[#1769AA] lg:mx-0 lg:justify-start">
              <ShieldCheck className="size-4 text-[#238636]" />
              <span>आपकी सुरक्षा हमारी प्राथमिकता है</span>
            </div>
          </div>

          {/* TWO COLUMN INTERACTION CONTAINER */}
          <div className="grid w-full max-w-4xl grid-cols-1 items-stretch gap-8 md:grid-cols-2">
            {/* COLUMN 1: VOICE ASSISTANT CARD */}
            <div className="relative flex flex-col justify-between overflow-hidden rounded-3xl border border-[#D9E1EC] bg-white p-6 shadow-xl transition-all duration-300 hover:shadow-2xl sm:p-8">
              {/* Header info inside card */}
              <div className="mb-4 flex w-full items-center justify-between border-b border-[#D9E1EC]/60 pb-4">
                <div className="flex items-center gap-3">
                  <div className="group relative cursor-pointer" onClick={handleCenterpieceClick}>
                    <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-blue-600 to-amber-500 opacity-40 blur transition duration-500 group-hover:opacity-75"></div>
                    <img
                      src="/avatar.png"
                      alt="Dhan Rakshak Avatar"
                      className="relative size-12 rounded-full border-2 border-[#1769AA]/20 object-cover shadow-md"
                    />
                    {isConnected && (
                      <span className="absolute right-0 bottom-0 size-3 animate-pulse rounded-full border-2 border-white bg-[#238636]" />
                    )}
                  </div>
                  <div className="text-left">
                    <h3 className="text-base font-extrabold text-[#12355B]">
                      Dhan Rakshak (धन रक्षक)
                    </h3>
                    <p className="text-[10px] font-bold tracking-wider text-[#5B667A] uppercase">
                      AI Security Agent
                    </p>
                  </div>
                </div>

                {/* State notification pill */}
                <div className="rounded-full border border-[#D9E1EC] bg-[#F5F8FC] px-3 py-1 text-xs font-bold text-[#12355B]">
                  {isConnected ? 'Active' : 'Offline'}
                </div>
              </div>

              {/* DYNAMIC CARD CONTENT */}
              <div className="flex w-full flex-col items-center justify-center py-4 text-center">
                {/* Ready State */}
                {!isConnected && !isConnecting && !callEnded && !micPermissionBlocked && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-bold text-[#12355B]">Ready to talk?</h4>
                    <p className="mx-auto max-w-xs text-xs text-[#5B667A]">
                      Ask me about banking, digital payments, financial schemes or banking safety.
                    </p>
                    <Button
                      onClick={handleCenterpieceClick}
                      className="mt-4 w-full rounded-xl bg-gradient-to-r from-[#1769AA] to-[#12355B] py-6 text-sm font-bold text-white shadow-md transition-all duration-200 hover:scale-105 active:scale-95"
                    >
                      Start Secure Conversation
                    </Button>
                  </div>
                )}

                {/* Connecting State */}
                {isConnecting && !isConnected && (
                  <div className="space-y-4">
                    <div className="mx-auto w-fit animate-pulse rounded-full bg-[#1769AA]/10 p-4">
                      <Loader2 className="size-10 animate-spin text-[#1769AA]" />
                    </div>
                    <h4 className="text-lg font-bold text-[#12355B]">Connecting securely…</h4>
                    <p className="mx-auto max-w-xs text-xs text-[#5B667A]">
                      Please wait while Dhan Rakshak joins the conversation.
                    </p>
                  </div>
                )}

                {/* Mic Permission Blocked State */}
                {micPermissionBlocked && (
                  <div className="space-y-4">
                    <div className="mx-auto w-fit rounded-full bg-[#C62828]/10 p-3">
                      <MicOff className="size-8 text-[#C62828]" />
                    </div>
                    <h4 className="text-base font-bold text-[#C62828]">
                      Microphone access is required
                    </h4>
                    <p className="mx-auto max-w-xs text-xs text-[#5B667A]">
                      Dhan Rakshak needs microphone access to have a voice conversation.
                    </p>
                    <Button
                      onClick={handleStartCall}
                      className="w-full rounded-xl bg-[#C62828] font-bold text-white hover:bg-[#C62828]/90"
                    >
                      Try Again
                    </Button>
                  </div>
                )}

                {/* Connected / Active Session (Listening or Speaking) */}
                {isConnected && (
                  <div className="w-full space-y-6">
                    {/* Default Voice Bar Visualizer */}
                    <div className="flex h-20 w-full items-center justify-center overflow-hidden">
                      <AudioVisualizer
                        audioVisualizerType="bar"
                        audioVisualizerColor={
                          resolvedTheme === 'dark'
                            ? appConfig.audioVisualizerColorDark
                            : appConfig.audioVisualizerColor
                        }
                        audioVisualizerBarCount={7}
                        isChatOpen={false}
                        className="h-16 w-48"
                      />
                    </div>

                    {/* Active Indicator & Speaker Name */}
                    <div className="space-y-2">
                      <div className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold tracking-wider uppercase">
                        {agentState === 'listening' ? (
                          <span className="flex items-center gap-1.5 text-[#1769AA]">
                            <span className="relative flex h-2 w-2">
                              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#1769AA] opacity-75"></span>
                              <span className="relative inline-flex h-2 w-2 rounded-full bg-[#1769AA]"></span>
                            </span>
                            Listening to you
                          </span>
                        ) : agentState === 'speaking' ? (
                          <span className="flex items-center gap-1.5 text-[#F28C28]">
                            <span className="relative flex h-2 w-2">
                              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#F28C28] opacity-75"></span>
                              <span className="relative inline-flex h-2 w-2 rounded-full bg-[#F28C28]"></span>
                            </span>
                            Dhan Rakshak is speaking
                          </span>
                        ) : agentState === 'thinking' ? (
                          <span className="animate-pulse text-[#12355B]">
                            Dhan Rakshak is thinking...
                          </span>
                        ) : (
                          <span className="text-[#5B667A]">Dhan Rakshak is ready</span>
                        )}
                      </div>
                      <p className="mx-auto max-w-xs text-xs font-semibold text-[#5B667A]">
                        {agentState === 'listening'
                          ? 'Speak naturally. I’m listening.'
                          : 'Listen to financial advice.'}
                      </p>
                    </div>

                    {/* Centerpiece Clickable Button to End Call */}
                    <div className="pt-2">
                      <Button
                        onClick={handleCenterpieceClick}
                        className="w-full rounded-xl bg-[#C62828] py-6 font-bold text-white hover:bg-[#C62828]/90"
                      >
                        <PhoneOff className="mr-2 size-4" /> End Secure Conversation
                      </Button>
                    </div>
                  </div>
                )}

                {/* Call Ended State */}
                {callEnded && !isConnected && (
                  <div className="w-full space-y-4">
                    <div className="mx-auto w-fit rounded-full bg-[#238636]/10 p-3">
                      <ShieldCheck className="size-8 text-[#238636]" />
                    </div>
                    <h4 className="text-lg font-bold text-[#12355B]">Conversation ended</h4>
                    <p className="mx-auto max-w-xs text-xs text-[#5B667A]">
                      Thank you for speaking with Dhan Rakshak.
                    </p>
                    <Button
                      onClick={handleCenterpieceClick}
                      className="w-full rounded-xl bg-[#1769AA] py-6 font-bold text-white hover:bg-[#12355B]"
                    >
                      Start Secure Conversation
                    </Button>
                    {/* Analytics CTA — visible after every call */}
                    <a
                      href="http://localhost:5050/analytics"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-[#1769AA]/30 py-3 text-sm font-bold text-[#1769AA] transition-all duration-200 hover:border-[#1769AA] hover:bg-[#1769AA]/5"
                    >
                      <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                      </svg>
                      View Call Analytics
                    </a>
                  </div>
                )}
              </div>

              {/* Language Selection Options */}
              <div className="mt-2 border-t border-[#D9E1EC]/60 pt-4">
                <div className="mb-2 flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1 font-bold text-[#12355B]">
                    <Globe className="size-3.5 text-[#1769AA]" /> Language Option / भाषा
                  </span>
                  <span className="font-semibold text-[#5B667A] capitalize">
                    {selectedLanguage}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setSelectedLanguage('hindi')}
                    className={`rounded-lg border px-2 py-1.5 text-xs font-bold transition-all ${
                      selectedLanguage === 'hindi'
                        ? 'border-[#12355B] bg-[#12355B] text-white shadow-sm'
                        : 'border-[#D9E1EC] bg-[#F5F8FC] text-[#5B667A] hover:bg-white'
                    }`}
                  >
                    Hindi / हिंदी
                  </button>
                  <button
                    onClick={() => setSelectedLanguage('english')}
                    className={`rounded-lg border px-2 py-1.5 text-xs font-bold transition-all ${
                      selectedLanguage === 'english'
                        ? 'border-[#12355B] bg-[#12355B] text-white shadow-sm'
                        : 'border-[#D9E1EC] bg-[#F5F8FC] text-[#5B667A] hover:bg-white'
                    }`}
                  >
                    English
                  </button>
                  <button
                    onClick={() => setSelectedLanguage('hinglish')}
                    className={`rounded-lg border px-2 py-1.5 text-xs font-bold transition-all ${
                      selectedLanguage === 'hinglish'
                        ? 'border-[#12355B] bg-[#12355B] text-white shadow-sm'
                        : 'border-[#D9E1EC] bg-[#F5F8FC] text-[#5B667A] hover:bg-white'
                    }`}
                  >
                    Hinglish
                  </button>
                </div>
              </div>
            </div>

            {/* COLUMN 2: LIVE TRANSCRIPT PANEL */}
            <div className="flex flex-col justify-between rounded-3xl border border-[#D9E1EC] bg-white p-6 shadow-xl transition-all duration-300 hover:shadow-2xl sm:p-8">
              <div>
                <h3 className="mb-1 flex items-center gap-2 border-b border-[#D9E1EC]/60 pb-3 text-base font-extrabold text-[#12355B]">
                  <svg
                    className="size-5 text-[#1769AA]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2.5"
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                  Live Conversation Transcript
                </h3>

                {/* Scrollable chat messages container */}
                <div className="mt-4 h-[260px] overflow-y-auto pr-1 [scrollbar-width:thin]">
                  {messages.length === 0 ? (
                    <div className="flex h-full flex-col items-center justify-center text-center text-[#5B667A] opacity-60">
                      <svg
                        className="mb-2 size-8"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="1.5"
                          d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                        />
                      </svg>
                      <p className="text-xs font-semibold">
                        No active conversation transcripts yet.
                      </p>
                      <p className="mt-1 text-[10px]">Start a call to see live transcripts here.</p>
                    </div>
                  ) : (
                    <AgentChatTranscript
                      agentState={agentState}
                      messages={messages}
                      className="[&_.is-user>div]:rounded-2xl [&>div]:px-1 md:[&>div]:px-2"
                    />
                  )}
                </div>
              </div>

              {/* Chat Input Box */}
              <div className="mt-2 border-t border-[#D9E1EC]/60 pt-4">
                {isConnected ? (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Ask Dhan Rakshak..."
                      value={chatText}
                      onChange={(e) => setChatText(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && chatText.trim()) {
                          send?.(chatText.trim());
                          setChatText('');
                        }
                      }}
                      className="flex-1 rounded-xl border border-[#D9E1EC] bg-[#F5F8FC]/50 px-4 py-2 text-xs transition-all focus:border-[#1769AA] focus:ring-2 focus:ring-[#1769AA]/50 focus:outline-none sm:text-sm"
                    />
                    <button
                      onClick={() => {
                        if (chatText.trim()) {
                          send?.(chatText.trim());
                          setChatText('');
                        }
                      }}
                      className="rounded-xl bg-[#12355B] px-4 py-2 text-xs font-bold text-white shadow-md transition-all hover:bg-[#1769AA] hover:shadow-lg active:scale-95 sm:text-sm"
                    >
                      Send
                    </button>
                  </div>
                ) : (
                  <p className="rounded-xl border border-[#D9E1EC]/60 bg-[#F5F8FC] py-2 text-center text-[10px] font-semibold text-[#5B667A]">
                    Start a call to write and ask Dhan Rakshak
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECURITY TRUST SECTION */}
      <section className="w-full border-y border-[#D9E1EC] bg-white py-12" id="safety">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto mb-10 max-w-xl text-center">
            <h2 className="mb-2 text-2xl font-extrabold text-[#12355B] sm:text-3xl">
              Your Safety Comes First
            </h2>
            <p className="text-xs text-[#5B667A] sm:text-sm">
              Dhan Rakshak will never ask for your OTP, PIN, CVV, password or complete account
              number.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 sm:gap-6 md:grid-cols-4">
            <div className="flex flex-col items-center rounded-2xl border border-[#D9E1EC] bg-[#F5F8FC] p-5 text-center">
              <div className="mb-4 rounded-xl bg-[#C62828]/10 p-3 text-[#C62828]">
                <Lock className="size-6" />
              </div>
              <h4 className="mb-1 text-sm font-extrabold text-[#12355B]">Never Share OTP</h4>
              <p className="text-[11px] leading-relaxed text-[#5B667A]">
                OTPs are confidential entry keys. Keep them private.
              </p>
            </div>

            <div className="flex flex-col items-center rounded-2xl border border-[#D9E1EC] bg-[#F5F8FC] p-5 text-center">
              <div className="mb-4 rounded-xl bg-[#C62828]/10 p-3 text-[#C62828]">
                <KeyRound className="size-6" />
              </div>
              <h4 className="mb-1 text-sm font-extrabold text-[#12355B]">Never Share PIN</h4>
              <p className="text-[11px] leading-relaxed text-[#5B667A]">
                Your ATM or UPI PIN belongs only to you.
              </p>
            </div>

            <div className="flex flex-col items-center rounded-2xl border border-[#D9E1EC] bg-[#F5F8FC] p-5 text-center">
              <div className="mb-4 rounded-xl bg-[#C62828]/10 p-3 text-[#C62828]">
                <Ban className="size-6" />
              </div>
              <h4 className="mb-1 text-sm font-extrabold text-[#12355B]">Never Share Password</h4>
              <p className="text-[11px] leading-relaxed text-[#5B667A]">
                Online banking passwords must remain secret.
              </p>
            </div>

            <div className="flex flex-col items-center rounded-2xl border border-[#D9E1EC] bg-[#F5F8FC] p-5 text-center">
              <div className="mb-4 rounded-xl bg-[#238636]/10 p-3 text-[#238636]">
                <Eye className="size-6" />
              </div>
              <h4 className="mb-1 text-sm font-extrabold text-[#12355B]">Verify Before You Pay</h4>
              <p className="text-[11px] leading-relaxed text-[#5B667A]">
                Check receiver details before authorizing money.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* DIGITAL ARREST AWARENESS BANNER */}
      <section className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8" id="digital">
        <div className="relative overflow-hidden rounded-3xl border border-[#1769AA]/20 bg-gradient-to-r from-[#12355B] to-[#1769AA] p-6 text-white shadow-lg sm:p-8">
          <div className="absolute top-0 right-0 size-48 translate-x-10 -translate-y-10 rounded-full bg-[#F28C28]/10 blur-2xl" />
          <div className="relative z-10 flex flex-col items-center justify-between gap-6 md:flex-row">
            <div className="flex items-start gap-4">
              <div className="rounded-2xl border border-[#F28C28]/30 bg-[#F28C28]/25 p-3 text-[#F28C28]">
                <AlertTriangle className="size-8" />
              </div>
              <div>
                <h3 className="mb-2 text-xl font-black tracking-tight sm:text-2xl">
                  Beware of Digital Arrest Scams
                </h3>
                <p className="max-w-2xl text-xs leading-relaxed font-medium text-white/80 sm:text-sm">
                  No genuine bank, police officer or government official will place you under
                  &quot;digital arrest&quot; or demand money through a video call.
                </p>
              </div>
            </div>
            <div className="rounded-2xl border border-white/20 bg-white/10 px-6 py-3 text-center backdrop-blur-sm">
              <span className="block text-[10px] font-extrabold tracking-widest text-[#F28C28] uppercase">
                Safety Mantra
              </span>
              <span className="text-lg font-black tracking-wide text-white uppercase">
                Stop. Verify. Report.
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* FINANCIAL SERVICES SECTION */}
      <section className="mx-auto w-full max-w-7xl px-4 py-16 sm:px-6 lg:px-8" id="schemes">
        <div className="mx-auto mb-12 max-w-xl text-center">
          <h2 className="mb-3 text-3xl font-extrabold text-[#12355B]">
            How Can Dhan Rakshak Help?
          </h2>
          <p className="text-sm font-semibold text-[#5B667A]">
            Click to start talking to Dhan Rakshak about any of these banking service themes.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <Landmark className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">Bank Accounts</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Understanding savings accounts, deposits, and low-cost schemes.
            </p>
          </div>

          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <Coins className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">Loans</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Explore official interest options and government loan initiatives.
            </p>
          </div>

          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <CreditCard className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">Digital Payments</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Secure mobile banking transactions, ATMs, and digital services.
            </p>
          </div>

          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <Shield className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">UPI Safety</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Rules for setting UPI PINs, scanning QR codes, and resolving bugs.
            </p>
          </div>

          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <ShieldCheck className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">Government Schemes</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Guidance for PM Jan Dhan Yojana, insurance schemes, and pensions.
            </p>
          </div>

          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <AlertTriangle className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">Fraud Awareness</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Avoid phishing, card cloning, KYC scams, and fake customer care.
            </p>
          </div>

          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <CreditCard className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">Credit & Debit Cards</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Understanding limits, chargebacks, and safe usage guidelines.
            </p>
          </div>

          <div
            className="group cursor-pointer rounded-2xl border border-[#D9E1EC] bg-white p-5 shadow-sm transition-all hover:border-[#1769AA]/40 hover:shadow-md"
            onClick={handleCenterpieceClick}
          >
            <div className="mb-4 w-fit rounded-xl bg-[#1769AA]/10 p-3 text-[#1769AA] transition-colors group-hover:bg-[#1769AA] group-hover:text-white">
              <GraduationCap className="size-6" />
            </div>
            <h4 className="mb-2 text-base font-extrabold text-[#12355B]">Financial Literacy</h4>
            <p className="text-xs leading-relaxed text-[#5B667A]">
              Basic savings planning, budgeting rules, and financial planning.
            </p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer
        className="mt-auto border-t border-[#1769AA]/20 bg-[#12355B] py-12 text-white"
        id="help"
      >
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-4 text-center sm:px-6 md:flex-row md:text-left lg:px-8">
          <div>
            <p className="text-sm font-semibold tracking-wide text-white/80">
              Technology should make banking simpler, safer, and accessible to everyone.
            </p>
            <p className="mt-1 text-xs text-white/50">
              Dhan Rakshak is an educational voice AI assistant. It cannot access accounts or
              process payments.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* Analytics Dashboard Link */}
            <a
              href="http://localhost:5050/analytics"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 rounded-xl border border-[#1769AA]/60 bg-[#1769AA] px-4 py-2 text-[11px] font-bold tracking-widest text-white uppercase transition-colors hover:bg-[#1769AA]/80"
            >
              <svg className="size-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              Call Analytics
            </a>
            <div className="flex items-center gap-1 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-[11px] font-bold tracking-widest text-white/60 uppercase">
              <ShieldCheck className="size-4 text-[#F28C28]" /> Secure Portal
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
