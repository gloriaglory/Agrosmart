import axios from "axios";

const BASE_URL = "https://your-api-url.com/api";

/**
 * Generic API call handler using Axios.
 * @param endpoint API route after base URL
 * @param method HTTP method (GET, POST, etc.)
 * @param data Optional data payload for POST/PUT
 */
export const callApi = async (
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data: unknown = null
): Promise<unknown> => {
  try {
    const response = await axios({
      url: `${BASE_URL}/${endpoint}`,
      method,
      data
    });
    return response.data;
  } catch (error) {
    console.error(`API error on ${endpoint}`, error);
    throw error;
  }
};

/**
 * Translate text using LibreTranslate API.
 * @param text Text to be translated
 * @param source Source language code (e.g., "en")
 * @param target Target language code (e.g., "sw")
 */
export const translateText = async (
  text: string,
  source: string,
  target: string
): Promise<string> => {
  const res = await fetch('https://libretranslate.com/translate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      q: text,
      source,
      target,
      format: 'text'
    })
  });

  const data = await res.json();
  return data.translatedText;
};
