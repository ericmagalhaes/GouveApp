declare module 'annyang' {
  interface CommandOption {
    (command: string): void;
  }

  interface Commands {
    [command: string]: CommandOption;
  }

  interface Annyang {
    abort: () => void;
    addCallback: (event: string, callback: (...args: any[]) => void) => void;
    addCommands: (commands: Commands) => void;
    debug: (enabled: boolean) => void;
    isListening: () => boolean;
    pause: () => void;
    resume: () => void;
    setLanguage: (language: string) => void;
    start: () => void;
  }

  const annyang: Annyang;

  export default annyang;
}
