<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { 
    chatHistory, 
    userMessage, 
    isAudioRecording, 
    isVideoRecording, 
    flashingButtons, 
    isLoading,
    selectedAgent,
    transcriptionError,
    responseError,
    selectedVoice,
    speechSpeed
  } from '../stores/stores';

  // Define the types of variables
  let chatWindow: HTMLDivElement | null = null;
  let audioRecorder: MediaRecorder | null = null;
  let audioChunks: Blob[] = [];
  let videoRecorder: MediaRecorder | null = null;
  let videoChunks: Blob[] = [];
  let audioBlob: Blob | null = null;
  let isProcessing: boolean = false;
  let audioPlayer: HTMLAudioElement | null = null;
  let lastAudioUrl: string | null = null;
  let videoStream: MediaStream | null = null;

  onMount(() => {
    if (chatWindow) {
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }
  });

  async function sendTextMessage(message: string, agentName: string) {
    isLoading.set(true);
    try {
      const payload = {
        prompt_text: message,
        agent_name: agentName
      };

      const response = await fetch('/api/multimedia/text/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.response_text) {
        chatHistory.update(history => {
          const newHistory = [...history, { text: message, isUser: true }, { text: data.response_text, isUser: false }];
          sessionStorage.setItem('lastConversation', JSON.stringify(newHistory));
          return newHistory;
        });
      } else {
        throw new Error("Unexpected response from API");
      }
    } catch (error) {
      handleError(error, responseError);
    } finally {
      isLoading.set(false);
    }
  }

  function handleMessage() {
    const message = get(userMessage);
    const activeAgent = get(selectedAgent);
    if (message.trim() && activeAgent && activeAgent.name) {
      sendTextMessage(message, activeAgent.name);
      userMessage.set('');
    }
  }

  async function handleTranscriptionAndSend() {
    if (isProcessing) return;

    isProcessing = true;
    isLoading.set(true);

    try {
      if (get(isAudioRecording)) {
        await stopAudioRecording();
      }

      if (audioChunks.length === 0) {
        transcriptionError.set('No audio recorded.');
        return;
      }

      const formData = new FormData();
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const audioFile = new File([blob], "audio.webm", { type: 'audio/webm' });
      formData.append('audio', audioFile);
      formData.append('agent_name', get(selectedAgent).name);

      const response = await fetch('/api/multimedia/deepgram_transcribe/', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      const transcription = data.transcription;

      if (transcription) {
        const llmResponse = await fetch('/api/multimedia/text/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            prompt_text: transcription,
            agent_name: get(selectedAgent).name
          })
        });

        const llmData = await llmResponse.json();
        if (llmData.response_text) {
          await synthesizeSpeech(llmData.response_text);
        }
      }
    } catch (error) {
      handleError(error, transcriptionError);
    } finally {
      isLoading.set(false);
      isAudioRecording.set(false);
      audioChunks = [];
      isProcessing = false;
    }
  }

  function toggleAudioRecording() {
    if (get(isAudioRecording)) {
      handleTranscriptionAndSend();
    } else {
      if (!audioRecorder) {
        setupAudioRecorder(audioChunks).then(() => {
          if (audioRecorder) {
            startAudioRecording();
          } else {
            handleError(new Error('Failed to initialize audio recorder'), transcriptionError);
          }
        });
      } else {
        if (audioRecorder.state === 'inactive') {
          startAudioRecording();
        }
      }
    }
  }

  function startAudioRecording() {
    if (!audioRecorder) {
      handleError(new Error('Audio recorder not initialized'), transcriptionError);
      return;
    }
    if (audioRecorder.state === 'inactive') {
      audioChunks = [];
      audioRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };
      audioRecorder.start();
      isAudioRecording.set(true);
    }
  }

  function stopAudioRecording(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!audioRecorder) {
        reject(new Error('Audio recorder not initialized'));
        return;
      }

      if (audioRecorder.state === 'recording') {
        audioRecorder.onstop = () => {
          audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          resolve();
        };

        audioRecorder.stop();
        isAudioRecording.set(false);
      } else {
        resolve();
      }
    });
  }

  function stopSpeaking() {
    if (audioPlayer) {
      audioPlayer.pause();
      audioPlayer.currentTime = 0;
    }
  }

  function sayItAgain() {
    if (!lastAudioUrl) {
      responseError.set('No previous audio to replay.');
      return;
    }

    const audio = new Audio(lastAudioUrl);
    audio.onerror = (event) => {
      if ((event.target as HTMLAudioElement).error?.code === 4) {
        responseError.set('Audio file not found.');
      } else {
        responseError.set('Error playing audio. Please try again.');
      }
    };

    if (audioPlayer) {
      audioPlayer.pause();
      audioPlayer = null;
    }
    audioPlayer = audio;
    audioPlayer.play();
    audioPlayer.onended = () => {
      audioPlayer = null;
    };
  }

  async function takePicture() {
    try {
      if (!videoStream) {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoElement = document.querySelector<HTMLVideoElement>('#video');
        if (videoElement) {
          videoElement.srcObject = videoStream;
          await new Promise(resolve => videoElement.onloadedmetadata = resolve);
        }
      }

      const canvas = document.createElement('canvas');
      const videoElement = document.querySelector<HTMLVideoElement>('#video');
      if (videoElement) {
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        canvas.getContext('2d')?.drawImage(videoElement, 0, 0);

        canvas.toBlob(async (blob) => {
          if (!blob) {
            transcriptionError.set('Failed to capture image.');
            return;
          }

          const selectedImageFile = new File([blob], "captured_image.png", { type: 'image/png' });
          await handleImageUpload(selectedImageFile);
        }, 'image/png');
      }
    } catch (error) {
      handleError(error, transcriptionError);
    }
  }

  function selectFile(type: string) {
    const input = document.createElement('input');
    input.type = 'file';
    if (type === 'text') input.accept = '.txt';
    if (type === 'pdf') input.accept = 'application/pdf';
    if (type === 'image') input.accept = 'image/png, image/jpeg';
    if (type === 'video') input.accept = 'video/mp4, video/webm';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        if (type === 'text') await handleTextFileUpload(file);
        if (type === 'pdf') await handlePdfUpload(file);
        if (type === 'image') await handleImageUpload(file);
        if (type === 'video') await handleVideoUpload(file);
      }
    };
    input.click();
  }

  async function resetChatSession() {
    try {
      const response = await fetch('/api/multimedia/reset-chat-session/', {
        method: 'POST'
      });

      if (response.ok) {
        chatHistory.set([]);
        sessionStorage.removeItem('lastConversation');

        const activeAgent = get(selectedAgent);
        if (activeAgent && activeAgent.name) {
          const message = "Starting a new session.";
          await sendTextMessage(message, activeAgent.name);
        }
      } else {
        throw new Error('Failed to reset chat session');
      }
    } catch (error) {
      handleError(error, responseError);
    }
  }

  function toggleVideoRecording() {
    if (get(isVideoRecording)) {
      stopVideoRecording();
    } else {
      if (!videoRecorder) {
        setupVideoRecorder().then(() => {
          if (videoRecorder) {
            startVideoRecording();
          } else {
            handleError(new Error('Failed to initialize video recorder'), transcriptionError);
          }
        });
      } else {
        if (videoRecorder.state === 'inactive') {
          startVideoRecording();
        }
      }
    }
  }

  function startVideoRecording() {
    if (!videoRecorder) {
      handleError(new Error('Video recorder not initialized'), transcriptionError);
      return;
    }
    if (videoRecorder.state === 'inactive') {
      videoChunks = [];
      videoRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          videoChunks.push(event.data);
        }
      };
      videoRecorder.start();
      isVideoRecording.set(true);
    }
  }

  function stopVideoRecording(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!videoRecorder) {
        reject(new Error('Video recorder not initialized'));
        return;
      }

      if (videoRecorder.state === 'recording') {
        videoRecorder.onstop = () => {
          const videoBlob = new Blob(videoChunks, { type: 'video/webm' });
          resolve();
        };

        videoRecorder.stop();
        isVideoRecording.set(false);
      } else {
        resolve();
      }
    });
  }

  async function setupAudioRecorder(audioChunks: Blob[]): Promise<MediaRecorder | null> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      let options: MediaRecorderOptions = { mimeType: 'audio/webm' };

      if (!MediaRecorder.isTypeSupported('audio/webm')) {
        if (MediaRecorder.isTypeSupported('audio/ogg')) {
          options = { mimeType: 'audio/ogg' };
        } else {
          options = {};
        }
      }
      
      const recorder = new MediaRecorder(stream, options);

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      audioRecorder = recorder;
      return recorder;
    } catch (error) {
      console.error('Error setting up audio recorder:', error);
      handleError(error, transcriptionError);
      return null;
    }
  }

  async function setupVideoRecorder(): Promise<MediaRecorder | undefined> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      const recorder = new MediaRecorder(stream);
      recorder.ondataavailable = (e) => {
        if (get(isVideoRecording)) videoChunks.push(e.data);
      };
      recorder.onstop = async () => {
        try {
          if (get(isVideoRecording)) {
            const videoBlob = new Blob(videoChunks, { type: 'video/mp4' });
            const selectedVideoFile = new File([videoBlob], "video.mp4", { type: 'video/mp4' });
            await handleVideoUpload(selectedVideoFile);
          }
        } catch (error) {
          handleError(error, transcriptionError);
        } finally {
          isVideoRecording.set(false);
          isLoading.set(false);
        }
      };
      videoRecorder = recorder;
      return recorder;
    } catch (error) {
      handleError(error, transcriptionError);
    }
  }

  async function handleImageUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/multimedia/upload-image', {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('Failed to upload image');
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function handleTextFileUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/multimedia/upload-text', {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('Failed to upload text file');
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function handlePdfUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/multimedia/upload-pdf', {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('Failed to upload PDF');
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function handleVideoUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/multimedia/upload-video', {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('Failed to upload video');
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function synthesizeSpeech(text: string) {
    try {
      const response = await fetch('/api/multimedia/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          voice: get(selectedVoice),
          speed: get(speechSpeed)
        })
      });

      const data = await response.json();
      if (data.audio_url) {
        lastAudioUrl = data.audio_url;
        const audio = new Audio(data.audio_url);
        audio.onerror = (event) => {
          if ((event.target as HTMLAudioElement).error?.code === 4) {
            responseError.set('Audio file not found.');
          } else {
            responseError.set('Error playing audio. Please try again.');
          }
        };
        if (audioPlayer) {
          audioPlayer.pause();
          audioPlayer = null;
        }
        audioPlayer = audio;
        audioPlayer.play();
        audioPlayer.onended = () => {
          audioPlayer = null;
        };
      } else {
        throw new Error("Failed to synthesize speech");
      }
    } catch (error) {
      handleError(error, responseError);
    }
  }

  function handleError(error: Error, store: typeof responseError) {
    console.error(error);
    store.set(error.message);
  }
</script>

<div class="flex flex-col h-[800px] bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl overflow-hidden">
  <!-- Chat Window -->
  <div class="flex-1 overflow-y-auto p-6" bind:this={chatWindow}>
    {#each $chatHistory as message}
      <div class="mb-4 {message.isUser ? 'flex justify-end' : 'flex justify-start'}">
        <div class="{message.isUser ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'} rounded-lg px-4 py-2 max-w-[80%] shadow-md">
          {message.text}
        </div>
      </div>
    {/each}
  </div>

  <!-- Input Area -->
  <div class="border-t dark:border-gray-700 p-4 bg-white/50 dark:bg-gray-800/50">
    <!-- Text Input -->
    <div class="flex gap-2 mb-4">
      <input
        type="text"
        bind:value={$userMessage}
        placeholder="Type your message..."
        class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        on:keypress={(e) => e.key === 'Enter' && handleMessage()}
      />
      <button
        on:click={handleMessage}
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
      >
        Send
      </button>
    </div>

    <!-- Media Controls -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
      <button
        on:click={toggleAudioRecording}
        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors flex items-center justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clip-rule="evenodd" />
        </svg>
        {$isAudioRecording ? 'Stop Recording' : 'Record Audio'}
      </button>

      <button
        on:click={toggleVideoRecording}
        class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors flex items-center justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
        </svg>
        {$isVideoRecording ? 'Stop Recording' : 'Record Video'}
      </button>

      <button
        on:click={takePicture}
        class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors flex items-center justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
        </svg>
        Take Picture
      </button>

      <button
        on:click={resetChatSession}
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors flex items-center justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
        New Chat
      </button>
    </div>

    <!-- Audio Controls -->
    <div class="grid grid-cols-2 gap-2 mb-4">
      <button
        on:click={sayItAgain}
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
      >
        Say it Again
      </button>
      <button
        on:click={stopSpeaking}
        class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
      >
        Stop Speaking
      </button>
    </div>

    <!-- File Upload Options -->
    <div class="grid grid-cols-3 gap-2">
      <button
        on:click={() => selectFile('text')}
        class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
      >
        Text File
      </button>
      <button
        on:click={() => selectFile('pdf')}
        class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
      >
        PDF File
      </button>
      <button
        on:click={() => selectFile('video')}
        class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 transition-colors"
      >
        Video File
      </button>
    </div>
  </div>
</div>

<!-- Hidden video element for camera capture -->
<video id="video" style="display: none;" playsinline>
  <track kind="captions" src="" label="English" default>
</video>
