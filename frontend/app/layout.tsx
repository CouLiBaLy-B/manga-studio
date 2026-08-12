import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'MangaTok Studio — Mode « Conte animé »',
  description: 'Génération de vidéos verticales manga avec cohérence visuelle et fiches canoniques',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased selection:bg-yellow-400 selection:text-black">
        {children}
      </body>
    </html>
  );
}
