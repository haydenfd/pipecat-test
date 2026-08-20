import '@fontsource-variable/geist';
import '@fontsource-variable/geist-mono';
import '@pipecat-ai/voice-ui-kit/styles';

import { ConsoleTemplate, ThemeProvider } from '@pipecat-ai/voice-ui-kit';
import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return (
    <ThemeProvider defaultTheme="dark">
      <div className="app-shell">
        <ConsoleTemplate
          transportType="smallwebrtc"
          connectParams={{ webrtcUrl: '/api/offer' }}
          noUserVideo
          noBotVideo
          noScreenControl
        />
      </div>
    </ThemeProvider>
  );
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
