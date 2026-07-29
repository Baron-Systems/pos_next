/**
 * Sound utility using the Web Audio API.
 * Generates audible beeps without external audio files.
 *
 * IMPORTANT: prepareAudioContext() must be called from a user gesture
 * (e.g. keydown, click) BEFORE any async work. Once the event handler
 * returns, the browser will block audio context resumption.
 */

let audioContext = null

function getAudioContext() {
	if (!audioContext) {
		audioContext = new (window.AudioContext || window.webkitAudioContext)()
	}
	return audioContext
}

/**
 * Prepare the audio context so it is ready to play sounds.
 * MUST be called from inside a user gesture handler (keydown, click, etc.).
 * Returns a Promise so the caller can await it before doing async work.
 */
export function prepareAudioContext() {
	const ctx = getAudioContext()
	if (ctx.state === "suspended") {
		return ctx.resume().catch(() => {})
	}
	return Promise.resolve()
}

/**
 * Play a loud, clear error beep to alert the user.
 * Uses two rapid descending tones for maximum recognizability.
 */
export function playErrorBeep() {
	try {
		const ctx = getAudioContext()
		if (ctx.state !== "running") {
			console.warn("AudioContext not running, cannot play beep")
			return
		}
		const now = ctx.currentTime

		// Warning pattern: 3 harsh sawtooth pulses with descending frequency
		// Pulse 1: high urgent tone
		const osc1 = ctx.createOscillator()
		const gain1 = ctx.createGain()
		osc1.type = "sawtooth"
		osc1.frequency.setValueAtTime(1000, now)
		osc1.frequency.exponentialRampToValueAtTime(800, now + 0.15)
		gain1.gain.setValueAtTime(1.0, now)
		gain1.gain.exponentialRampToValueAtTime(0.01, now + 0.15)
		osc1.connect(gain1)
		gain1.connect(ctx.destination)
		osc1.start(now)
		osc1.stop(now + 0.15)

		// Pulse 2: medium tone (short gap)
		const osc2 = ctx.createOscillator()
		const gain2 = ctx.createGain()
		osc2.type = "sawtooth"
		osc2.frequency.setValueAtTime(800, now + 0.20)
		osc2.frequency.exponentialRampToValueAtTime(600, now + 0.35)
		gain2.gain.setValueAtTime(1.0, now + 0.20)
		gain2.gain.exponentialRampToValueAtTime(0.01, now + 0.35)
		osc2.connect(gain2)
		gain2.connect(ctx.destination)
		osc2.start(now + 0.20)
		osc2.stop(now + 0.35)

		// Pulse 3: low final tone (short gap)
		const osc3 = ctx.createOscillator()
		const gain3 = ctx.createGain()
		osc3.type = "sawtooth"
		osc3.frequency.setValueAtTime(600, now + 0.40)
		osc3.frequency.exponentialRampToValueAtTime(400, now + 0.55)
		gain3.gain.setValueAtTime(1.0, now + 0.40)
		gain3.gain.exponentialRampToValueAtTime(0.01, now + 0.55)
		osc3.connect(gain3)
		gain3.connect(ctx.destination)
		osc3.start(now + 0.40)
		osc3.stop(now + 0.55)
	} catch (error) {
		console.warn("Failed to play error beep:", error)
	}
}

/**
 * Play a short success beep.
 */
export function playSuccessBeep() {
	try {
		const ctx = getAudioContext()
		if (ctx.state !== "running") {
			console.warn("AudioContext not running, cannot play beep")
			return
		}
		const now = ctx.currentTime
		const osc = ctx.createOscillator()
		const gain = ctx.createGain()
		osc.type = "sine"
		osc.frequency.setValueAtTime(1200, now)
		gain.gain.setValueAtTime(0.5, now)
		gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1)
		osc.connect(gain)
		gain.connect(ctx.destination)
		osc.start(now)
		osc.stop(now + 0.1)
	} catch (error) {
		console.warn("Failed to play success beep:", error)
	}
}
