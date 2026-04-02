/**
 * TRIBE v2 Persona Predictor - API Client
 * Connects React frontend to FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8003';

class ApiClient {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const mergedOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, mergedOptions);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      // Handle different response types
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      return await response.blob();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/api/health');
  }

  // List available personas
  async getPersonas() {
    const result = await this.request('/api/personas');
    return result.personas;
  }

  // Analyze video file
  async analyzeVideo(file, persona = 'analytical', onProgress = null, useTribe = false) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('persona', persona);
    formData.append('use_tribe', useTribe.toString());

    // Use XMLHttpRequest for progress tracking with longer timeout
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      // Set timeout based on mode (TRIBE v2 takes longer)
      xhr.timeout = useTribe ? 900000 : 60000; // 15 min for TRIBE, 1 min for fallback
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const percentComplete = Math.round((e.loaded / e.total) * 100);
          onProgress({ stage: 'uploading', percent: percentComplete });
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const result = JSON.parse(xhr.responseText);
            resolve(result);
          } catch (e) {
            reject(new Error('Invalid response format'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || `Analysis failed: ${xhr.status}`));
          } catch (e) {
            reject(new Error(`Analysis failed: ${xhr.status}`));
          }
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'));
      });

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload cancelled'));
      });

      xhr.addEventListener('timeout', () => {
        reject(new Error('Analysis timed out. Video may be too long or TRIBE v2 processing is taking too long.'));
      });

      // Start the request
      xhr.open('POST', `${this.baseUrl}/api/analyze/video`);
      
      if (onProgress) {
        onProgress({ stage: 'processing', percent: 50 });
      }

      xhr.send(formData);
    });
  }

  // Get video stream URL
  getVideoUrl(videoId) {
    return `${this.baseUrl}/api/videos/${videoId}`;
  }

  // Delete video
  async deleteVideo(videoId) {
    return this.request(`/api/videos/${videoId}`, {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
const api = new ApiClient();

export default api;
export { ApiClient };
