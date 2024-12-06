import { uploadFiles } from '../services/fileUploadService';
import axios from '../config/axiosConfig';

jest.mock('../config/axiosConfig', () => ({
  post: jest.fn()
}));

describe('File Upload Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should upload files successfully', async () => {
    // Mock successful response
    const mockResponse = {
      data: {
        files: [
          {
            filename: 'test.txt',
            document_id: 1,
            file_location: '/uploads/test.txt'
          }
        ]
      }
    };

    (axios.post as jest.Mock).mockResolvedValueOnce(mockResponse);

    // Create test file
    const testContent = 'Test file content';
    const blob = new Blob([testContent], { type: 'text/plain' });
    const testFile = new File([blob], 'test.txt', { type: 'text/plain' });

    // Test upload
    const result = await uploadFiles([testFile]);

    // Verify results
    expect(result).toEqual(mockResponse.data.files);
    expect(axios.post).toHaveBeenCalledTimes(1);
  });

  it('should handle upload errors', async () => {
    // Mock error response
    const mockError = {
      response: {
        status: 500,
        data: { detail: 'Server error' }
      }
    };

    (axios.post as jest.Mock).mockRejectedValueOnce(mockError);

    // Create test file
    const testContent = 'Test file content';
    const blob = new Blob([testContent], { type: 'text/plain' });
    const testFile = new File([blob], 'test.txt', { type: 'text/plain' });

    // Test upload and expect error
    await expect(uploadFiles([testFile])).rejects.toThrow('Error 500: Server error');
    expect(axios.post).toHaveBeenCalledTimes(1);
  });

  it('should validate file size', async () => {
    // Create large file
    const largeContent = new Array(11 * 1024 * 1024).join('a'); // > 10MB
    const blob = new Blob([largeContent], { type: 'text/plain' });
    const largeFile = new File([blob], 'large.txt', { type: 'text/plain' });

    // Test upload with large file
    await expect(uploadFiles([largeFile])).rejects.toThrow('No hay archivos válidos para subir');
    expect(axios.post).not.toHaveBeenCalled();
  });

  it('should validate file type', async () => {
    // Create file with invalid type
    const testContent = 'Test content';
    const blob = new Blob([testContent], { type: 'invalid/type' });
    const invalidFile = new File([blob], 'invalid.xyz', { type: 'invalid/type' });

    // Test upload with invalid file type
    await expect(uploadFiles([invalidFile])).rejects.toThrow('No hay archivos válidos para subir');
    expect(axios.post).not.toHaveBeenCalled();
  });
});
