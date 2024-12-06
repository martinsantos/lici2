import { uploadFiles } from '../services/fileUploadService';
import axios from '../config/axiosConfig';
import { API_CONFIG } from '../config/apiConfig';

jest.mock('../config/axiosConfig', () => ({
  post: jest.fn()
}));

const originalWarn = console.warn;

describe('File Upload Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    console.warn = jest.fn();
  });

  afterEach(() => {
    console.warn = originalWarn;
  });

  it('should upload files successfully', async () => {
    // Mock successful response
    const mockResponse = {
      data: {
        files: [
          {
            filename: 'test.pdf',
            document_id: 1,
            file_location: '/uploads/test.pdf'
          }
        ]
      }
    };

    (axios.post as jest.Mock).mockResolvedValueOnce(mockResponse);

    // Create test file
    const testContent = 'Test file content';
    const blob = new Blob([testContent], { type: 'application/pdf' });
    const testFile = new File([blob], 'test.pdf', { 
      type: 'application/pdf', 
      lastModified: Date.now() 
    });

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

    (axios.post as jest.Mock)
      .mockRejectedValueOnce(mockError)
      .mockRejectedValueOnce(mockError)
      .mockRejectedValueOnce(mockError);

    // Create test file
    const testContent = 'Test file content';
    const blob = new Blob([testContent], { type: 'application/pdf' });
    const testFile = new File([blob], 'test.pdf', { 
      type: 'application/pdf', 
      lastModified: Date.now() 
    });

    // Test upload and expect error
    await expect(uploadFiles([testFile])).rejects.toThrow('Error 500: Server error');
    expect(axios.post).toHaveBeenCalledTimes(3);
  });

  it('should validate file size', async () => {
    // Mock File object to control size
    const mockLargeFile = {
      name: 'large.pdf',
      type: 'application/pdf',
      size: API_CONFIG.UPLOAD_CONFIG.MAX_FILE_SIZE + 1,
      lastModified: Date.now()
    } as File;

    // Spy on console.warn
    const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

    // Test upload with large file
    try {
      await uploadFiles([mockLargeFile]);
      fail('Expected an error to be thrown');
    } catch (error: unknown) {
      if (error instanceof Error) {
        expect(error.message).toBe('No hay archivos válidos para subir');
      } else {
        fail('Expected an Error object');
      }
    }
    
    // Verify warning was logged
    expect(warnSpy).toHaveBeenCalledTimes(1);
    const warnMessage = warnSpy.mock.calls[0][0];
    
    // Detailed assertions on warning message
    const maxSizeMB = API_CONFIG.UPLOAD_CONFIG.MAX_FILE_SIZE / (1024 * 1024);
    expect(warnMessage).toMatch(new RegExp(`El archivo large\\.pdf excede el tamaño máximo permitido de ${maxSizeMB.toFixed(2)} MB \\(${API_CONFIG.UPLOAD_CONFIG.MAX_FILE_SIZE} bytes\\). Tamaño actual: ${mockLargeFile.size} bytes`));
    
    // Verify axios was not called
    expect(axios.post).not.toHaveBeenCalled();

    // Restore console.warn
    warnSpy.mockRestore();
  });

  it('should validate file type', async () => {
    // Create file with invalid type
    const testContent = 'Test content';
    const blob = new Blob([testContent], { type: 'invalid/type' });
    const invalidFile = new File([blob], 'invalid.xyz', { 
      type: 'invalid/type',
      lastModified: Date.now() 
    });

    // Test upload with invalid file type
    await expect(uploadFiles([invalidFile])).rejects.toThrow('No hay archivos válidos para subir');
    
    // Verify warning was logged
    expect(console.warn).toHaveBeenCalledWith(expect.stringContaining('tipo no permitido'));
    
    // Verify axios was not called
    expect(axios.post).not.toHaveBeenCalled();
  });

  it('should limit number of files', async () => {
    // Create more files than allowed
    const files = Array.from({ length: API_CONFIG.UPLOAD_CONFIG.MAX_FILES + 1 }, (_, i) => {
      const testContent = `Test content ${i}`;
      const blob = new Blob([testContent], { type: 'application/pdf' });
      return new File([blob], `test${i}.pdf`, { 
        type: 'application/pdf',
        lastModified: Date.now() 
      });
    });

    // Test upload with too many files
    await expect(uploadFiles(files)).rejects.toThrow(`No se pueden subir más de ${API_CONFIG.UPLOAD_CONFIG.MAX_FILES} archivos`);
    
    // Verify axios was not called
    expect(axios.post).not.toHaveBeenCalled();
  });
});
