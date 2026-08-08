'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext, useTrackToggle, useVoiceAssistant, useSessionMessages } from '@livekit/components-react';
import { Track } from 'livekit-client';
import { 
  ShieldCheck, Loader2, RefreshCw, AlertTriangle, Shield, Landmark, 
  CreditCard, Lock, Eye, KeyRound, Ban, HelpCircle, Mic, MicOff, 
  Info, Coins, GraduationCap, Award, PhoneOff, Globe
} from 'lucide-react';
import type { AppConfig } from '@/app-config';
import { AudioVisualizer } from '@/components/agents-ui/blocks/agent-session-view-01/components/audio-visualizer';
import { AgentChatTranscript } from '@/components/agents-ui/agent-chat-transcript';
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
  const { messages } = useSessionMessages(session);

  const [micPermissionBlocked, setMicPermissionBlocked] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [hasConnectedOnce, setHasConnectedOnce] = useState(false);
  const [callEnded, setCallEnded] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<'hindi' | 'english' | 'hinglish'>('hindi');

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
    } catch (err: any) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
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
    <div className="min-h-screen bg-[#F5F8FC] text-[#172033] w-full flex flex-col font-sans selection:bg-[#F28C28]/20 selection:text-[#12355B] relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#e5effa_1px,transparent_1px),linear-gradient(to_bottom,#e5effa_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-60 pointer-events-none" />

      {/* HEADER */}
      <header className="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-[#D9E1EC] transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-[#12355B] text-white p-2 rounded-xl shadow-md border-2 border-white">
              <svg className="size-6 text-[#F28C28]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <div className="flex items-baseline gap-1.5">
                <span className="font-bold text-lg text-[#12355B]">धन रक्षक</span>
                <span className="text-[#5B667A] text-xs font-semibold">Dhan Rakshak</span>
              </div>
              <div className="hidden sm:inline-block bg-[#1769AA]/10 text-[#1769AA] text-[10px] px-2 py-0.5 rounded-full font-bold border border-[#1769AA]/20 uppercase tracking-wider">
                Secure AI Financial Assistant
              </div>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-semibold text-[#5B667A]">
            <a href="#safety" className="hover:text-[#12355B] transition-colors">Banking Safety</a>
            <a href="#digital" className="hover:text-[#12355B] transition-colors">Digital Payments</a>
            <a href="#schemes" className="hover:text-[#12355B] transition-colors">Financial Schemes</a>
            <a href="#help" className="hover:text-[#12355B] transition-colors">Help</a>
          </nav>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="relative pt-12 pb-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-12">
          <div className="max-w-xl text-center lg:text-left">
            <span className="inline-flex items-center gap-1.5 bg-[#F28C28]/10 text-[#F28C28] text-xs font-bold px-3 py-1 rounded-full border border-[#F28C28]/20 mb-4">
              <Award className="size-3.5" /> सुरक्षित बैंकिंग, सरल मार्गदर्शन
            </span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#12355B] leading-[1.1] mb-4">
              Your Trusted Guide to <span className="text-[#1769AA]">Safe Banking</span>
            </h1>
            <p className="text-base md:text-lg text-[#5B667A] font-medium mb-6">
              Understand banking, digital payments and financial services through a simple voice conversation.
            </p>
            <div className="flex items-center justify-center lg:justify-start gap-2 text-xs font-bold text-[#1769AA] bg-[#1769AA]/5 border border-[#1769AA]/10 px-4 py-2 rounded-xl w-fit mx-auto lg:mx-0">
              <ShieldCheck className="size-4 text-[#238636]" />
              <span>आपकी सुरक्षा हमारी प्राथमिकता है</span>
            </div>
          </div>

          {/* TWO COLUMN INTERACTION CONTAINER */}
          <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch">
            
            {/* COLUMN 1: VOICE ASSISTANT CARD */}
            <div className="bg-white border border-[#D9E1EC] rounded-3xl shadow-xl p-6 sm:p-8 flex flex-col justify-between relative overflow-hidden transition-all duration-300 hover:shadow-2xl">
              {/* Header info inside card */}
              <div className="flex items-center justify-between w-full border-b border-[#D9E1EC]/60 pb-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="relative group cursor-pointer" onClick={handleCenterpieceClick}>
                    <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-amber-500 rounded-full blur opacity-40 group-hover:opacity-75 transition duration-500"></div>
                    <img
                      src="/avatar.png"
                      alt="Dhan Rakshak Avatar"
                      className="relative rounded-full size-12 object-cover border-2 border-[#1769AA]/20 shadow-md"
                    />
                    {isConnected && (
                      <span className="absolute bottom-0 right-0 size-3 rounded-full bg-[#238636] border-2 border-white animate-pulse" />
                    )}
                  </div>
                  <div className="text-left">
                    <h3 className="font-extrabold text-[#12355B] text-base">Dhan Rakshak (धन रक्षक)</h3>
                    <p className="text-[#5B667A] text-[10px] uppercase font-bold tracking-wider">AI Security Agent</p>
                  </div>
                </div>

                {/* State notification pill */}
                <div className="text-xs font-bold text-[#12355B] bg-[#F5F8FC] px-3 py-1 rounded-full border border-[#D9E1EC]">
                  {isConnected ? 'Active' : 'Offline'}
                </div>
              </div>

              {/* DYNAMIC CARD CONTENT */}
              <div className="w-full flex flex-col items-center justify-center text-center py-4">
                
                {/* Ready State */}
                {!isConnected && !isConnecting && !callEnded && !micPermissionBlocked && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-bold text-[#12355B]">Ready to talk?</h4>
                    <p className="text-xs text-[#5B667A] max-w-xs mx-auto">
                      Ask me about banking, digital payments, financial schemes or banking safety.
                    </p>
                    <Button
                      onClick={handleCenterpieceClick}
                      className="w-full mt-4 rounded-xl font-bold bg-gradient-to-r from-[#1769AA] to-[#12355B] text-white hover:scale-105 active:scale-95 transition-all duration-200 shadow-md py-6 text-sm"
                    >
                      Start Secure Conversation
                    </Button>
                  </div>
                )}

                {/* Connecting State */}
                {isConnecting && !isConnected && (
                  <div className="space-y-4">
                    <div className="bg-[#1769AA]/10 p-4 rounded-full w-fit mx-auto animate-pulse">
                      <Loader2 className="size-10 text-[#1769AA] animate-spin" />
                    </div>
                    <h4 className="text-lg font-bold text-[#12355B]">Connecting securely…</h4>
                    <p className="text-xs text-[#5B667A] max-w-xs mx-auto">
                      Please wait while Dhan Rakshak joins the conversation.
                    </p>
                  </div>
                )}

                {/* Mic Permission Blocked State */}
                {micPermissionBlocked && (
                  <div className="space-y-4">
                    <div className="bg-[#C62828]/10 p-3 rounded-full w-fit mx-auto">
                      <MicOff className="size-8 text-[#C62828]" />
                    </div>
                    <h4 className="text-base font-bold text-[#C62828]">Microphone access is required</h4>
                    <p className="text-xs text-[#5B667A] max-w-xs mx-auto">
                      Dhan Rakshak needs microphone access to have a voice conversation.
                    </p>
                    <Button
                      onClick={handleStartCall}
                      className="w-full rounded-xl font-bold bg-[#C62828] hover:bg-[#C62828]/90 text-white"
                    >
                      Try Again
                    </Button>
                  </div>
                )}

                {/* Connected / Active Session (Listening or Speaking) */}
                {isConnected && (
                  <div className="w-full space-y-6">
                    {/* Default Voice Bar Visualizer */}
                    <div className="flex justify-center items-center h-20 w-full overflow-hidden">
                      <AudioVisualizer
                        audioVisualizerType="bar"
                        audioVisualizerColor={resolvedTheme === 'dark' ? appConfig.audioVisualizerColorDark : appConfig.audioVisualizerColor}
                        audioVisualizerBarCount={7}
                        isChatOpen={false}
                        className="h-16 w-48"
                      />
                    </div>

                    {/* Active Indicator & Speaker Name */}
                    <div className="space-y-2">
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                        {agentState === 'listening' ? (
                          <span className="flex items-center gap-1.5 text-[#1769AA]">
                            <span className="relative flex h-2 w-2">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#1769AA] opacity-75"></span>
                              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#1769AA]"></span>
                            </span>
                            Listening to you
                          </span>
                        ) : agentState === 'speaking' ? (
                          <span className="flex items-center gap-1.5 text-[#F28C28]">
                            <span className="relative flex h-2 w-2">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#F28C28] opacity-75"></span>
                              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#F28C28]"></span>
                            </span>
                            Dhan Rakshak is speaking
                          </span>
                        ) : agentState === 'thinking' ? (
                          <span className="text-[#12355B] animate-pulse">Dhan Rakshak is thinking...</span>
                        ) : (
                          <span className="text-[#5B667A]">Dhan Rakshak is ready</span>
                        )}
                      </div>
                      <p className="text-xs text-[#5B667A] font-semibold max-w-xs mx-auto">
                        {agentState === 'listening' ? 'Speak naturally. I’m listening.' : 'Listen to financial advice.'}
                      </p>
                    </div>

                    {/* Centerpiece Clickable Button to End Call */}
                    <div className="pt-2">
                      <Button
                        onClick={handleCenterpieceClick}
                        className="w-full rounded-xl font-bold bg-[#C62828] hover:bg-[#C62828]/90 text-white py-6"
                      >
                        <PhoneOff className="size-4 mr-2" /> End Secure Conversation
                      </Button>
                    </div>
                  </div>
                )}

                {/* Call Ended State */}
                {callEnded && !isConnected && (
                  <div className="space-y-4 w-full">
                    <div className="bg-[#238636]/10 p-3 rounded-full w-fit mx-auto">
                      <ShieldCheck className="size-8 text-[#238636]" />
                    </div>
                    <h4 className="text-lg font-bold text-[#12355B]">Conversation ended</h4>
                    <p className="text-xs text-[#5B667A] max-w-xs mx-auto">
                      Thank you for speaking with Dhan Rakshak.
                    </p>
                    <Button
                      onClick={handleCenterpieceClick}
                      className="w-full rounded-xl font-bold bg-[#1769AA] hover:bg-[#12355B] text-white py-6"
                    >
                      Start Secure Conversation
                    </Button>
                  </div>
                )}
              </div>

              {/* Language Selection Options */}
              <div className="border-t border-[#D9E1EC]/60 pt-4 mt-2">
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className="font-bold text-[#12355B] flex items-center gap-1">
                    <Globe className="size-3.5 text-[#1769AA]" /> Language Option / भाषा
                  </span>
                  <span className="text-[#5B667A] font-semibold capitalize">{selectedLanguage}</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setSelectedLanguage('hindi')}
                    className={`py-1.5 px-2 rounded-lg text-xs font-bold border transition-all ${
                      selectedLanguage === 'hindi'
                        ? 'bg-[#12355B] text-white border-[#12355B] shadow-sm'
                        : 'bg-[#F5F8FC] text-[#5B667A] border-[#D9E1EC] hover:bg-white'
                    }`}
                  >
                    Hindi / हिंदी
                  </button>
                  <button
                    onClick={() => setSelectedLanguage('english')}
                    className={`py-1.5 px-2 rounded-lg text-xs font-bold border transition-all ${
                      selectedLanguage === 'english'
                        ? 'bg-[#12355B] text-white border-[#12355B] shadow-sm'
                        : 'bg-[#F5F8FC] text-[#5B667A] border-[#D9E1EC] hover:bg-white'
                    }`}
                  >
                    English
                  </button>
                  <button
                    onClick={() => setSelectedLanguage('hinglish')}
                    className={`py-1.5 px-2 rounded-lg text-xs font-bold border transition-all ${
                      selectedLanguage === 'hinglish'
                        ? 'bg-[#12355B] text-white border-[#12355B] shadow-sm'
                        : 'bg-[#F5F8FC] text-[#5B667A] border-[#D9E1EC] hover:bg-white'
                    }`}
                  >
                    Hinglish
                  </button>
                </div>
              </div>
            </div>

            {/* COLUMN 2: LIVE TRANSCRIPT PANEL */}
            <div className="bg-white border border-[#D9E1EC] rounded-3xl shadow-xl p-6 sm:p-8 flex flex-col justify-between transition-all duration-300 hover:shadow-2xl">
              <div>
                <h3 className="font-extrabold text-[#12355B] text-base mb-1 flex items-center gap-2 border-b border-[#D9E1EC]/60 pb-3">
                  <svg className="size-5 text-[#1769AA]" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  Live Conversation Transcript
                </h3>
                
                {/* Scrollable chat messages container */}
                <div className="h-[260px] overflow-y-auto mt-4 pr-1 [scrollbar-width:thin]">
                  {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-[#5B667A] opacity-60">
                      <svg className="size-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                      <p className="text-xs font-semibold">No active conversation transcripts yet.</p>
                      <p className="text-[10px] mt-1">Start a call to see live transcripts here.</p>
                    </div>
                  ) : (
                    <AgentChatTranscript
                      agentState={agentState}
                      messages={messages as any}
                      className="[&_.is-user>div]:rounded-2xl [&>div]:px-1 md:[&>div]:px-2"
                    />
                  )}
                </div>
              </div>

              {/* Safety notice in the transcript column footer */}
              <div className="border-t border-[#D9E1EC]/60 pt-4 text-[10px] text-[#5B667A] font-semibold text-center mt-2 flex items-center gap-1.5 justify-center">
                <ShieldCheck className="size-4 text-[#238636]" /> Confidential financial conversation guidance.
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* SECURITY TRUST SECTION */}
      <section className="bg-white border-y border-[#D9E1EC] py-12 w-full" id="safety">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-xl mx-auto mb-10">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#12355B] mb-2">Your Safety Comes First</h2>
            <p className="text-xs sm:text-sm text-[#5B667A]">
              Dhan Rakshak will never ask for your OTP, PIN, CVV, password or complete account number.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
            <div className="bg-[#F5F8FC] border border-[#D9E1EC] rounded-2xl p-5 text-center flex flex-col items-center">
              <div className="bg-[#C62828]/10 text-[#C62828] p-3 rounded-xl mb-4">
                <Lock className="size-6" />
              </div>
              <h4 className="font-extrabold text-sm text-[#12355B] mb-1">Never Share OTP</h4>
              <p className="text-[11px] text-[#5B667A] leading-relaxed">OTPs are confidential entry keys. Keep them private.</p>
            </div>

            <div className="bg-[#F5F8FC] border border-[#D9E1EC] rounded-2xl p-5 text-center flex flex-col items-center">
              <div className="bg-[#C62828]/10 text-[#C62828] p-3 rounded-xl mb-4">
                <KeyRound className="size-6" />
              </div>
              <h4 className="font-extrabold text-sm text-[#12355B] mb-1">Never Share PIN</h4>
              <p className="text-[11px] text-[#5B667A] leading-relaxed">Your ATM or UPI PIN belongs only to you.</p>
            </div>

            <div className="bg-[#F5F8FC] border border-[#D9E1EC] rounded-2xl p-5 text-center flex flex-col items-center">
              <div className="bg-[#C62828]/10 text-[#C62828] p-3 rounded-xl mb-4">
                <Ban className="size-6" />
              </div>
              <h4 className="font-extrabold text-sm text-[#12355B] mb-1">Never Share Password</h4>
              <p className="text-[11px] text-[#5B667A] leading-relaxed">Online banking passwords must remain secret.</p>
            </div>

            <div className="bg-[#F5F8FC] border border-[#D9E1EC] rounded-2xl p-5 text-center flex flex-col items-center">
              <div className="bg-[#238636]/10 text-[#238636] p-3 rounded-xl mb-4">
                <Eye className="size-6" />
              </div>
              <h4 className="font-extrabold text-sm text-[#12355B] mb-1">Verify Before You Pay</h4>
              <p className="text-[11px] text-[#5B667A] leading-relaxed">Check receiver details before authorizing money.</p>
            </div>
          </div>
        </div>
      </section>

      {/* DIGITAL ARREST AWARENESS BANNER */}
      <section className="py-8 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" id="digital">
        <div className="bg-gradient-to-r from-[#12355B] to-[#1769AA] text-white rounded-3xl p-6 sm:p-8 relative overflow-hidden shadow-lg border border-[#1769AA]/20">
          <div className="absolute right-0 top-0 translate-x-10 -translate-y-10 size-48 bg-[#F28C28]/10 rounded-full blur-2xl" />
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
            <div className="flex items-start gap-4">
              <div className="bg-[#F28C28]/25 text-[#F28C28] p-3 rounded-2xl border border-[#F28C28]/30">
                <AlertTriangle className="size-8" />
              </div>
              <div>
                <h3 className="text-xl sm:text-2xl font-black mb-2 tracking-tight">Beware of Digital Arrest Scams</h3>
                <p className="text-xs sm:text-sm text-white/80 leading-relaxed max-w-2xl font-medium">
                  No genuine bank, police officer or government official will place you under "digital arrest" or demand money through a video call.
                </p>
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm border border-white/20 px-6 py-3 rounded-2xl text-center">
              <span className="block text-[10px] font-extrabold uppercase tracking-widest text-[#F28C28]">Safety Mantra</span>
              <span className="font-black text-lg tracking-wide uppercase text-white">Stop. Verify. Report.</span>
            </div>
          </div>
        </div>
      </section>

      {/* FINANCIAL SERVICES SECTION */}
      <section className="py-16 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" id="schemes">
        <div className="text-center max-w-xl mx-auto mb-12">
          <h2 className="text-3xl font-extrabold text-[#12355B] mb-3">How Can Dhan Rakshak Help?</h2>
          <p className="text-sm text-[#5B667A] font-semibold">
            Click to start talking to Dhan Rakshak about any of these banking service themes.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <Landmark className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">Bank Accounts</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Understanding savings accounts, deposits, and low-cost schemes.</p>
          </div>

          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <Coins className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">Loans</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Explore official interest options and government loan initiatives.</p>
          </div>

          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <CreditCard className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">Digital Payments</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Secure mobile banking transactions, ATMs, and digital services.</p>
          </div>

          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <Shield className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">UPI Safety</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Rules for setting UPI PINs, scanning QR codes, and resolving bugs.</p>
          </div>

          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <ShieldCheck className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">Government Schemes</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Guidance for PM Jan Dhan Yojana, insurance schemes, and pensions.</p>
          </div>

          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <AlertTriangle className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">Fraud Awareness</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Avoid phishing, card cloning, KYC scams, and fake customer care.</p>
          </div>

          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <CreditCard className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">Credit & Debit Cards</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Understanding limits, chargebacks, and safe usage guidelines.</p>
          </div>

          <div className="bg-white border border-[#D9E1EC] hover:border-[#1769AA]/40 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group cursor-pointer" onClick={handleCenterpieceClick}>
            <div className="bg-[#1769AA]/10 text-[#1769AA] group-hover:bg-[#1769AA] group-hover:text-white p-3 rounded-xl w-fit transition-colors mb-4">
              <GraduationCap className="size-6" />
            </div>
            <h4 className="font-extrabold text-base text-[#12355B] mb-2">Financial Literacy</h4>
            <p className="text-xs text-[#5B667A] leading-relaxed">Basic savings planning, budgeting rules, and financial planning.</p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="mt-auto bg-[#12355B] text-white border-t border-[#1769AA]/20 py-12" id="help">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
          <div>
            <p className="text-sm font-semibold tracking-wide text-white/80">
              Technology should make banking simpler, safer, and accessible to everyone.
            </p>
            <p className="text-xs text-white/50 mt-1">
              Dhan Rakshak is an educational voice AI assistant. It cannot access accounts or process payments.
            </p>
          </div>
          <div className="flex items-center gap-1 text-[11px] font-bold text-white/60 bg-white/5 px-4 py-2 rounded-xl border border-white/10 uppercase tracking-widest">
            <ShieldCheck className="size-4 text-[#F28C28]" /> Secure Portal
          </div>
        </div>
      </footer>
    </div>
  );
}
