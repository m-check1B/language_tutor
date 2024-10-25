<script lang="ts">
    import { _ } from 'svelte-i18n';
    import { chatStore } from '$lib/stores/chat';
    import { onMount } from 'svelte';

    let videoStream: MediaStream | null = null;
    let videoElement: HTMLVideoElement;
    let selectedFile: File | null = null;
    let isSilentMode = false;
    let selectedVoice = 'alloy';
    let speechSpeed = 1.0;
    let availableVoices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'];

    onMount(() => {
        if (videoElement) {
            setupVideoPreview();
        }
    });

    async function setupVideoPreview() {
        try {
            videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoElement.srcObject = videoStream;
        } catch (error) {
            console.error('Error accessing camera:', error);
        }
    }

    async function takePicture() {
        if (!videoStream) return;

        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        canvas.getContext('2d')?.drawImage(videoElement, 0, 0);

        canvas.toBlob(async (blob) => {
            if (!blob) return;
            const imageFile = new File([blob], "captured_image.png", { type: 'image/png' });
            await handleFileUpload(imageFile, 'image');
        }, 'image/png');
    }

    async function handleFileUpload(file: File, type: string) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);

        try {
            const response = await fetch('/api/chat/file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Failed to upload file');

            const data = await response.json();
            chatStore.addMessage(`Uploaded ${type} file: ${file.name}`, true);
            if (data.response) {
                chatStore.addMessage(data.response, false);
                if (!isSilentMode && data.audioUrl) {
                    const audio = new Audio(data.audioUrl);
                    audio.playbackRate = speechSpeed;
                    await audio.play();
                }
            }
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    }

    function selectFile(type: string) {
        const input = document.createElement('input');
        input.type = 'file';
        switch (type) {
            case 'text':
                input.accept = '.txt';
                break;
            case 'pdf':
                input.accept = 'application/pdf';
                break;
            case 'image':
                input.accept = 'image/png, image/jpeg';
                break;
            case 'video':
                input.accept = 'video/mp4, video/webm';
                break;
            case 'audio':
                input.accept = 'audio/*';
                break;
        }

        input.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
                await handleFileUpload(file, type);
            }
        };
        input.click();
    }

    function updateTTSSettings() {
        chatStore.updateTTSSettings({
            voice: selectedVoice,
            speed: speechSpeed,
            isSilentMode
        });
    }
</script>

<div class="media-interface space-y-4">
    <!-- Video Preview -->
    <div class="video-preview">
        <video 
            bind:this={videoElement}
            autoplay 
            playsinline 
            class="w-full max-h-[200px] object-cover rounded-lg"
        >
            <track kind="captions">
        </video>
    </div>

    <!-- Media Controls -->
    <div class="flex flex-wrap gap-2">
        <button 
            class="btn-secondary"
            on:click={takePicture}
        >
            {$_('media.takePicture', { default: 'Take Picture' })}
        </button>

        <button 
            class="btn-secondary"
            on:click={() => selectFile('image')}
        >
            {$_('media.uploadImage', { default: 'Upload Image' })}
        </button>

        <button 
            class="btn-secondary"
            on:click={() => selectFile('video')}
        >
            {$_('media.uploadVideo', { default: 'Upload Video' })}
        </button>

        <button 
            class="btn-secondary"
            on:click={() => selectFile('audio')}
        >
            {$_('media.uploadAudio', { default: 'Upload Audio' })}
        </button>

        <button 
            class="btn-secondary"
            on:click={() => selectFile('text')}
        >
            {$_('media.uploadText', { default: 'Upload Text' })}
        </button>

        <button 
            class="btn-secondary"
            on:click={() => selectFile('pdf')}
        >
            {$_('media.uploadPdf', { default: 'Upload PDF' })}
        </button>
    </div>

    <!-- TTS Settings -->
    <div class="tts-settings bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
        <h3 class="text-lg font-semibold mb-2">
            {$_('tts.settings', { default: 'Text-to-Speech Settings' })}
        </h3>
        
        <div class="space-y-2">
            <label class="flex items-center gap-2">
                <input 
                    type="checkbox" 
                    bind:checked={isSilentMode}
                    on:change={updateTTSSettings}
                >
                {$_('tts.silentMode', { default: 'Silent Mode' })}
            </label>

            <div class="flex items-center gap-2">
                <label for="voice-select">
                    {$_('tts.voice', { default: 'Voice' })}:
                </label>
                <select 
                    id="voice-select"
                    bind:value={selectedVoice}
                    on:change={updateTTSSettings}
                    class="select-field"
                >
                    {#each availableVoices as voice}
                        <option value={voice}>{voice}</option>
                    {/each}
                </select>
            </div>

            <div class="flex items-center gap-2">
                <label for="speed-input">
                    {$_('tts.speed', { default: 'Speed' })}:
                </label>
                <input 
                    type="range"
                    id="speed-input"
                    min="0.5"
                    max="2.0"
                    step="0.1"
                    bind:value={speechSpeed}
                    on:change={updateTTSSettings}
                    class="range-field"
                >
                <span>{speechSpeed}x</span>
            </div>
        </div>
    </div>
</div>

<style>
    .media-interface {
        @apply w-full max-w-2xl mx-auto;
    }

    .btn-secondary {
        @apply px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg 
               hover:bg-gray-300 dark:hover:bg-gray-600 
               transition-colors duration-200;
    }

    .select-field {
        @apply px-2 py-1 rounded-lg bg-white dark:bg-gray-700 
               border border-gray-300 dark:border-gray-600;
    }

    .range-field {
        @apply w-32;
    }
</style>
