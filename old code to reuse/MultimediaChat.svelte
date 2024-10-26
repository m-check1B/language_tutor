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

      const response = await apiPost(`/api/multimedia/text/`, payload, {
        params: {
          include_response: true
        }
      });

      if (response.data.response_text) {
        chatHistory.update(history => {
          const newHistory = [...history, { text: message, isUser: true }, { text: response.data.response_text, isUser: false }];
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
    if (isProcessing) {
      return;
    }

    isProcessing = true;
    isLoading.set(true);

    try {
      if (get(isAudioRecording)) {
        await stopAudioRecording();
      }

      if (audioChunks.length === 0) {
        transcriptionError.set('No audio recorded.');
        isProcessing = false;
        isLoading.set(false);
        return;
      }

      const formData = new FormData();
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const audioFile = new File([blob], "audio.webm", { type: 'audio/webm' });

      formData.append('audio', audioFile);
      formData.append('agent_name', get(selectedAgent).name);

      const transcriptionResponse = await apiPost(`/api/multimedia/deepgram_transcribe/`, formData);

      const transcription = transcriptionResponse.data.transcription;

      if (transcription) {
        const llmResponse = await apiPost(`/api/multimedia/text/`, {
          prompt_text: transcription,
          agent_name: get(selectedAgent).name
        }, {
          params: {
            include_response: true 
          }
        });

        if (llmResponse.data && llmResponse.data.response_text) {
          const responseText = llmResponse.data.response_text;
          await synthesizeSpeech(responseText);
        } else if (llmResponse.data.message === "Request received and queued for processing") {
          console.log('LLM response queued, waiting for actual response.');
        } else {
          transcriptionError.set('Unexpected response from API');
        }
      } else {
        throw new Error("Received null transcription from API");
      }
    } catch (error) {
      transcriptionError.set((error as Error).message);
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
        } else {
          console.warn('Audio recorder is already recording');
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
    } else {
      console.warn('Audio recorder is already recording');
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
    if (type === 'video') input.accept = 'video/mp4, video/x-flv, video/mov, video/mpeg, video/mpegps, video/webm, video/wmv, video/3gpp';
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
      const response = await apiPost(`/api/multimedia/reset-chat-session/`);

      if (response.status === 200) {
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
        } else {
          console.warn('Video recorder is already recording');
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
    } else {
      console.warn('Video recorder is already recording');
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

      recorder.onstop = () => {
        console.log('MediaRecorder stopped, data available:', audioChunks);
      };

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
      console.log('Video recorder setup successful');
      const videoRecorder = new MediaRecorder(stream);
      videoRecorder.ondataavailable = (e) => {
        if (get(isVideoRecording)) videoChunks.push(e.data);
      };
      videoRecorder.onstop = async () => {
        console.log('Video recorder stopped');
        try {
          if (get(isVideoRecording)) {
            console.log('Preparing to send video');
            const videoBlob = new Blob(videoChunks, { type: 'video/mp4' });
            const selectedVideoFile = new File([videoBlob], "video.mp4", { type: 'video/mp4' });
            await handleVideoUpload(selectedVideoFile);
            console.log('Video upload completed');
          } else {
            console.log('Recording state (video) was false, not sending video');
          }
        } catch (error) {
          handleError(error, transcriptionError);
        } finally {
          isVideoRecording.set(false);
          isLoading.set(false);
        }
      };
      return videoRecorder;
    } catch (error) {
      handleError(error, transcriptionError);
    }
  }

  async function handleImageUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiPost(`/api/multimedia/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('Image uploaded successfully:', response.data);
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function handleTextFileUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiPost(`/api/multimedia/upload-text`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('Text file uploaded successfully:', response.data);
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function handlePdfUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiPost(`/api/multimedia/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('PDF uploaded successfully:', response.data);
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function handleVideoUpload(file: File) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiPost(`/api/multimedia/upload-video`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log('Video uploaded successfully:', response.data);
    } catch (error) {
      handleError(error, responseError);
    }
  }

  async function synthesizeSpeech(text: string) {
    try {
      const response = await apiPost(`/api/multimedia/synthesize`, {
        text: text,
        voice: get(selectedVoice),
        speed: get(speechSpeed)
      });
      if (response.data.audio_url) {
        const audioUrl = response.data.audio_url;
        lastAudioUrl = audioUrl;
        const audio = new Audio(audioUrl);
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

  async function apiPost(url: string, data: any, config: RequestInit = {}): Promise<any> {
    const response = await fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
    });
    return response.json();
  }
</script>

<div class="chat-section">
  <div class="chat-window" bind:this={chatWindow}>
    {#each $chatHistory as message}
      <p class={message.isUser ? 'user' : 'assistant'}>{message.text}</p>
    {/each}
  </div>
  <div class="message-input">
    <input type="text" bind:value={$userMessage} placeholder="Type your message here..." />
    <button on:click={handleMessage} class:flash={$flashingButtons.has('send-message-button')}>
      Text Message
    </button>
  </div>
  <div class="media-buttons">
    <button on:click={toggleAudioRecording} class:flash={$flashingButtons.has('toggle-audio-recording-button')}>
      {$isAudioRecording ? 'Stop Recording' : 'Audio Message'}
    </button>
    <button on:click={handleTranscriptionAndSend} class:flash={$flashingButtons.has('transcribe-and-send-button')}>
      Transcribe and Send
    </button>
    <button on:click={sayItAgain} class:flash={$flashingButtons.has('say-again-button')}>
      Say it Again
    </button>
    <button on:click={stopSpeaking} class:flash={$flashingButtons.has('stop-speaking-button')}>
      Stop Speaking
    </button>
    <button on:click={takePicture} class:flash={$flashingButtons.has('take-picture-button')}>
      Take a Picture
    </button>
    <button on:click={toggleVideoRecording} class:flash={$flashingButtons.has('toggle-video-recording-button')}>
      {$isVideoRecording ? 'Stop Recording' : 'Video Message'}
    </button>
    <button on:click={() => selectFile('text')} class:flash={$flashingButtons.has('select-text-file-button')}>
      Send Text File
    </button>
    <button on:click={() => selectFile('image')} class:flash={$flashingButtons.has('select-image-file-button')}>
      Send Image File
    </button>
    <button on:click={() => selectFile('audio')} class:flash={$flashingButtons.has('select-audio-file-button')}>
      Send Audio File
    </button>
    <button on:click={() => selectFile('video')} class:flash={$flashingButtons.has('select-video-file-button')}>
      Send Video File
    </button>
    <button on:click={() => selectFile('pdf')} class:flash={$flashingButtons.has('select-pdf-file-button')}>
      Send PDF File
    </button>
    <button on:click={resetChatSession} class:flash={$flashingButtons.has('reset-session-button')}>
      New Chat
    </button>
  </div>
</div>

<style>
  .chat-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .chat-window {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px;
    background: #D0E8D8;
    border-radius: 5px;
    border: 2px solid #556B2F;
    height: 400px; /* Adjust as needed */
  }
  
  .message-input {
    display: flex;
    gap: 10px;
  }
  
  .message-input input {
    flex-grow: 1;
    padding: 10px;
    border-radius: 5px;
    border: 2px solid #556B2F;
    background: #C2D2C0;
  }
  
  .message-input button {
    padding: 10px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    background-color: #50C878;
    color: #FFFFF0;
  }
  
  .media-buttons {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .media-buttons button {
    flex-grow: 1;
    padding: 10px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    background-color: #50C878;
    color: #FFFFF0;
    text-align: center;
  }
  
  .flash {
    animation: flash 0.5s ease-in-out;
  }
  
  @keyframes flash {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
</style>
