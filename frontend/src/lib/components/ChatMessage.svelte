<script lang="ts">
    export let message: string;
    export let isUser: boolean;
    export let timestamp: string;
    export let audioUrl: string | null = null;

    let isPlaying = false;
    let audio: HTMLAudioElement | null = null;

    function playAudio() {
        if (!audio && audioUrl) {
            audio = new Audio(audioUrl);
            audio.onended = () => {
                isPlaying = false;
            };
        }
        
        if (audio) {
            if (isPlaying) {
                audio.pause();
                isPlaying = false;
            } else {
                audio.play();
                isPlaying = true;
            }
        }
    }
</script>

<div class="flex {isUser ? 'justify-end' : 'justify-start'} mb-4">
    <div class="max-w-[80%] {isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-700'} rounded-lg p-3">
        {#if audioUrl}
            <button 
                on:click={playAudio}
                class="flex items-center gap-2 text-sm"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    {#if isPlaying}
                        <path d="M10 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1z" />
                        <path d="M4 8a1 1 0 011-1h2a1 1 0 010 2H5a1 1 0 01-1-1z" />
                        <path d="M14 8a1 1 0 100 2h2a1 1 0 100-2h-2z" />
                    {:else}
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
                    {/if}
                </svg>
                {isPlaying ? 'Pause Audio' : 'Play Audio'}
            </button>
        {:else}
            <p class="text-sm break-words">{message}</p>
        {/if}
        <div class="text-xs opacity-70 mt-1">
            {timestamp}
        </div>
    </div>
</div>
