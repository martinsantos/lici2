import { uploadFiles } from '../services/fileUploadService';

async function testFileUpload() {
    try {
        // Create a test file
        const testContent = 'Test file content';
        const blob = new Blob([testContent], { type: 'text/plain' });
        const testFile = new File([blob], 'test.txt', { type: 'text/plain' });

        console.log('Starting file upload test...');
        
        // Test file upload
        const response = await uploadFiles([testFile]);
        
        console.log('Upload successful:', response);
        return response;
    } catch (error) {
        console.error('Upload test failed:', error);
        throw error;
    }
}

// Run the test
testFileUpload()
    .then(result => {
        console.log('Test completed successfully:', result);
    })
    .catch(error => {
        console.error('Test failed:', error);
    });
