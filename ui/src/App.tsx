import React, { useCallback, useEffect, useState } from 'react';
import annyang from 'annyang';
import './App.css';

const App: React.FC = () => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const handleSpeechInput = useCallback((input: string) => {
    Promise.resolve({
      data: {
        videoUrl: 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
      },
    }).then(({ data }) => {
      setVideoUrl(data.videoUrl);
    });
  }, []);

  useEffect(() => {
    if (annyang) {
      const commands = {
        'Let me ask *input': (input: string) => {
          handleSpeechInput(input);
        },
      };

      annyang.debug(true);
      annyang.setLanguage('en-US');
      annyang.addCommands(commands);

      return () => {
        annyang.abort();
      };
    }
  }, [handleSpeechInput]);

  useEffect(() => {
    if (videoUrl !== null && annyang) {
      annyang.abort();
    }

    if (videoUrl === null && annyang && !annyang.isListening()) {
      annyang.start();
    }
  }, [videoUrl]);

  return (
    <div className="h-screen w-full flex items-center justify-center">
      {videoUrl === null && (
        <p className="text-center">
          Say "Let me ask" to start.
        </p>
      )}

      {videoUrl !== null && (
        <video
          autoPlay
          controls
          src={videoUrl}
          onEnded={() => {
            setVideoUrl(null);
          }}
        />
      )}
    </div>
  );
};

export default App;
