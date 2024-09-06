import React, { useCallback, useEffect, useState } from 'react';
import annyang from 'annyang';
import { axiosClient } from './axios';
import { KEYWORD_TRIGGER, LOCALE } from './config';

export const App: React.FC = () => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const handleSpeechInput = useCallback((input: string) => {
    axiosClient.post('/search', {
      query: input,
    })
      .then((response) => {
        console.log(response);
        setVideoUrl('http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4');
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  useEffect(() => {
    if (annyang) {
      const commands = {
        [`${KEYWORD_TRIGGER} *input`]: (input: string) => {
          handleSpeechInput(input);
        },
      };

      annyang.setLanguage(LOCALE);
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
          "{KEYWORD_TRIGGER}..."
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
