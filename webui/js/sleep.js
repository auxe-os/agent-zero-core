/**
 * Asynchronously waits for a specified duration. Handles long durations by
 * breaking them into smaller chunks to avoid issues with `setTimeout` limits.
 * @param {number} [miliseconds=0] - The number of milliseconds to wait.
 * @param {number} [seconds=0] - The number of seconds to wait.
 * @param {number} [minutes=0] - The number of minutes to wait.
 * @param {number} [hours=0] - The number of hours to wait.
 * @param {number} [days=0] - The number of days to wait.
 */
export async function sleep(miliseconds = 0, seconds = 0, minutes = 0, hours = 0, days = 0) {
  hours += days * 24;
  minutes += hours * 60;
  seconds += minutes * 60;
  miliseconds += seconds * 1000;
  
  // Maximum safe timeout is 1 hour (in milliseconds)
  const MAX_TIMEOUT = 60 * 60 * 1000;
  
  // if miliseconds is 0, wait at least one frame
  if (miliseconds === 0) {
    await new Promise((resolve) => setTimeout(resolve, 0));
    return;
  }

  // If the timeout is too large, break it into smaller chunks
  while (miliseconds > 0) {
    // Calculate the current chunk duration (1 hour max)
    const chunkDuration = Math.min(miliseconds, MAX_TIMEOUT);
    
    // Wait for the current chunk
    await new Promise((resolve) => setTimeout(resolve, chunkDuration));
    
    // Subtract the time we've waited
    miliseconds -= chunkDuration;
  }
}
export default sleep;

/**
 * Conditionally yields control back to the event loop after a certain number of
 * iterations. This is useful for preventing long-running synchronous-like loops
 * from blocking the main thread.
 * @param {number} [afterIterations=1] - The number of times this function must be
 * called before it actually yields.
 */
let yieldIterations = 0;
export async function Yield(afterIterations = 1) {
  yieldIterations++;
  if (yieldIterations >= afterIterations) {
    await new Promise((resolve) => setTimeout(resolve, 0));
    yieldIterations = 0;
  }
}

/**
 * Awaits the equivalent of `sleep(0)` a specified number of times.
 * This can be used to intentionally skip a number of frames or turns in the
 * JavaScript event queue.
 * @param {number} [turns=1] - The number of event loop turns to skip.
 */
export async function Skip(turns = 1) {
  while (turns > 0) {
    await new Promise((resolve) => setTimeout(resolve, 0));
    turns--;
  }
}