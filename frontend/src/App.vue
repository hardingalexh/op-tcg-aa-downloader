<script setup>
import {ref, onMounted} from "vue";
const URL_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"
const session_id = ref("")
const deckShareLink = ref("")
const images = ref([])

onMounted(async () => {
  const newSession = await fetch(`${URL_BASE}/create_session`).then(d => d.json())
  session_id.value = newSession
  })

async function fetchImages() {
  const imageList = await fetch(`${URL_BASE}/images/${session_id.value}`).then(d => d.json())
  images.value = imageList
}

async function submitDeck(){
  const postData = {
    'session_id': session_id.value,
    'deck': deckShareLink.value
  }
const submission = await fetch(`${URL_BASE}/submit_deck/`, {
  method: 'POST', // Specify the method
  headers: {
      'Content-Type': 'application/json; charset=UTF-8'
  },
  body: JSON.stringify(postData)
})
.then(response => response.json()) // Parse the JSON response
console.log(submission)

// Fetch updated images after submission
await fetchImages()
deckShareLink.value = ""
}

async function downloadZip() {
  const response = await fetch(`${URL_BASE}/download/${session_id.value}`)
  if (!response.ok) {
    alert('Failed to download zip file')
    return
  }

  const blob = await response.blob()
  const downloadUrl = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = `session-${session_id.value}.zip`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(downloadUrl)
}

</script>

<template>
  <div class="min-h-screen bg-gray-100 py-8 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <h1 class="text-3xl font-bold text-center text-gray-800 mb-2">OPTCGSim AA Downloader</h1>
      <p class="text-center text-gray-500 text-sm mb-8">Session: <span class="font-mono">{{ session_id }}</span></p>

      <!-- Step Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- Step 1: Set Up Deck -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-bold shrink-0">1</span>
            <h2 class="text-lg font-semibold text-gray-800">Set Up Deck(s) in Bandai TCG+</h2>
          </div>
          <div class="text-gray-600 text-sm leading-relaxed space-y-2">
            <p>Create your deck(s) in the <a class="linkfont-medium text-fg-brand hover:underline" href="https://www.bandai-tcg-plus.com/my_deck" target="_blank">Bandai TCG+ App.</a> This application will extract the alternate art images from your deck and download them in a structured format for inclusion in the OPTCGSim.</p>
            <p>You can upload multiple decks in a single session. Decks don't need to be valid for play - you can also create a deck that just contains the alt arts you'd like to include.</p>
          </div>
        </div>

        <!-- Step 2: Upload Deck(s) -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-bold shrink-0">2</span>
            <h2 class="text-lg font-semibold text-gray-800">Upload Deck(s)</h2>
          </div>
          <p class="text-gray-600 text-sm mb-4">Paste your Bandai TCG+ deck share link below and click submit. Repeat for each deck you want to include.</p>
          <p>For each deck you'd like to upload, copy the Facebook or X share link by right-clicking the Facebook/X images and selecting "copy link address".</p>
          <img src="/copy-link.png" />
          <hr />
          <div class="flex gap-2">
            <input
              type="text"
              v-model="deckShareLink"
              placeholder="Paste Bandai TCG+ Facebook or X share link…"
              class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              type="button"
              @click="submitDeck"
              class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg px-4 py-2 transition-colors cursor-pointer"
            >Submit</button>
          </div>
        </div>

        <!-- Step 3: Download Zip -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-bold shrink-0">3</span>
            <h2 class="text-lg font-semibold text-gray-800">Download Zip</h2>
          </div>

          <div v-if="images.length === 0" class="text-gray-400 text-sm italic">No images yet — submit a deck link in Step 2.</div>

          <div v-else>
            <div class="flex items-center justify-between mb-3">
              <span class="text-gray-600 text-sm">{{ images.length }} image{{ images.length !== 1 ? 's' : '' }} ready. When you are done uploading decks, download the zip archive.</span>
              <button
                @click="downloadZip"
                class="bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg px-4 py-2 transition-colors cursor-pointer"
              >Download Zip</button>
            </div>
            <div class="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-72 overflow-y-auto">
              <div v-for="image in images" :key="image" class="flex items-center justify-center">
                <img :src="`${URL_BASE}/image/${session_id}/${image}`" :alt="image" class="max-w-full h-auto rounded shadow-sm" />
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4: Extract & Upload -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex items-center gap-3 mb-4">
            <span class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white text-sm font-bold shrink-0">4</span>
            <h2 class="text-lg font-semibold text-gray-800">Extract &amp; Upload to Your Local Machine</h2>
          </div>
          <div class="text-gray-600 text-sm leading-relaxed space-y-2">
            <p>Once downloaded and unzipped, add these images to your local OPTCGSim.</p>
            <hr />
            <strong>Windows</strong>:
              <ol>
                <li>Locate your OPTCGSim app</li>
                <li>Navigate to \Builds_Windows\OPTCGSim_Data\StreamingAssets\Cards\</li>
                <li>Paste the contents of the zip file, choosing the "merge" option</li>
              </ol>
            <hr />
            <strong>Mac</strong>:
              <ol>
                <li>Locate your OPTCGSim app</li>
                <li>Right-click and choose "Show Package Contents"</li>
                <li>Navigate to Contents/Resources/Data/StreamingAssets/Cards</li>
                <li>Paste the contents of the zip file, choosing the "merge" option</li>
              </ol>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
