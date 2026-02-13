/**
 * Utility to get authentication headers for API requests
 */

import { auth } from './firebase';

/**
 * Get authentication headers with Firebase ID token
 * 
 * @returns Headers object with Authorization header
 * @throws Error if user is not authenticated
 */
export async function getAuthHeaders(): Promise<HeadersInit> {
  const user = auth.currentUser;
  
  if (!user) {
    throw new Error('User not authenticated');
  }

  const token = await user.getIdToken();

  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
}

/**
 * Get authentication headers or return default headers if not authenticated
 * 
 * @returns Headers object with or without Authorization header
 */
export async function getAuthHeadersOptional(): Promise<HeadersInit> {
  try {
    return await getAuthHeaders();
  } catch {
    return {
      'Content-Type': 'application/json',
    };
  }
}
