import confetti, { type Options } from "canvas-confetti";

/**
 * Utility function to create a random number within a range
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {number} Random number between min and max
 */
const randomInRange = (min: number, max: number): number => Math.random() * (max - min) + min;

interface ConfettiOptions {
	duration?: number;
	particleCount?: number;
	startVelocity?: number;
	spread?: number;
}

/**
 * Triggers a celebratory confetti animation
 * @param {ConfettiOptions} options - Configuration options for the confetti
 */
export const triggerCelebrationConfetti = (options: ConfettiOptions = {}) => {
	const { duration = 3000, particleCount = 50, startVelocity = 30, spread = 360 } = options;

	const animationEnd = Date.now() + duration;

	const interval = setInterval(() => {
		const timeLeft = animationEnd - Date.now();

		if (timeLeft <= 0) {
			clearInterval(interval);
			return;
		}

		const currentParticleCount = Math.floor(particleCount * (timeLeft / duration));

		// Left side confetti burst
		confetti({
			particleCount: currentParticleCount,
			startVelocity,
			spread,
			origin: {
				x: randomInRange(0.1, 0.3),
				y: Math.random() - 0.2,
			},
		});

		// Right side confetti burst
		confetti({
			particleCount: currentParticleCount,
			startVelocity,
			spread,
			origin: {
				x: randomInRange(0.7, 0.9),
				y: Math.random() - 0.2,
			},
		});
	}, 250);
};

/**
 * Triggers a simple single-burst confetti animation
 * @param {Options} options - Configuration options from canvas-confetti
 */
export const triggerSimpleConfetti = (options: Options = {}) => {
	const {
		particleCount = 100,
		startVelocity = 30,
		spread = 360,
		origin = { x: 0.5, y: 0.5 },
	} = options;

	confetti({
		particleCount,
		startVelocity,
		spread,
		origin,
	});
};
