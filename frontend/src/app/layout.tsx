import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'Animaker AI | Video-to-Animation Remake Studio',
  description: 'AI Video Animation Remake Engine powered by Gemini 2.5 Flash, Veo, Pollinations & Edge-TTS',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen flex flex-col bg-[#08070d] text-slate-100">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 md:p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
