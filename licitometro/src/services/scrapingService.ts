import { Template, ScrapingResult } from '../types/recon';
import { apiClient } from '../utils/apiClient';

export class ScrapingService {
  private static instance: ScrapingService;
  private baseUrl = '/api/scraping';

  private constructor() {}

  public static getInstance(): ScrapingService {
    if (!ScrapingService.instance) {
      ScrapingService.instance = new ScrapingService();
    }
    return ScrapingService.instance;
  }

  async startScraping(template: Template, url: string): Promise<string> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/start`, { template, url });
      return response.data.jobId;
    } catch (error) {
      console.error('Error starting scraping job:', error);
      throw error;
    }
  }

  async getScrapingStatus(jobId: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress?: number;
    result?: ScrapingResult;
  }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/status/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting scraping status:', error);
      throw error;
    }
  }

  async getScrapingResults(jobId: string): Promise<ScrapingResult> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/results/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting scraping results:', error);
      throw error;
    }
  }

  async cancelScraping(jobId: string): Promise<void> {
    try {
      await apiClient.post(`${this.baseUrl}/cancel/${jobId}`);
    } catch (error) {
      console.error('Error canceling scraping job:', error);
      throw error;
    }
  }
}
