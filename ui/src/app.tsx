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
      .then((response: any) => {
        console.log(response);
        setVideoUrl('https://ryzesc01.blob.core.windows.net/videos/'+encodeURI(response.data.results[0].payload.video));
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);
  const handleWelcome = useCallback((input: string) => {

      setVideoUrl('https://ryzesc01.blob.core.windows.net/videos/Welcome.mp4');

  }, []);

  useEffect(() => {
    if (annyang) {
      const commands = {
        [`${KEYWORD_TRIGGER} *input`]: (input: string) => {
          handleSpeechInput(input);
        },
        [`Oi Alê`]: (input: string) => {
          handleWelcome(input);
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
    <div className="h-screen w-full flex items-center justify-center player">
        <video
          autoPlay
          controls={true}
          src={videoUrl !== null ? videoUrl : ''}
          muted={false}
          onEnded={() => {
            setVideoUrl(null);
          }}
          style={{ display: videoUrl !== null ? 'block' : 'none' }}

        />

        <video
        autoPlay={true}
        controls={false}
        loop={true}
        src='https://ryzesc01.blob.core.windows.net/videos/Blinking_Eyes.mp4'
        muted={true}

        style={{ display: videoUrl === null ? 'block' : 'none' }}
      />

    </div>
  );
};
