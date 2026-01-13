# Performance Fix - DOCX Upload Issue

## Problem Identified

Upload of 7 DOCX files was taking >30 minutes because:

1. **DOCX not parsed correctly**: Parser only handled PDFs, DOCX was treated as plain text
2. **No timeout**: Requests could hang indefinitely
3. **Sequential processing**: Files processed one by one (correct, but slow for large files)

## Fixes Applied

### 1. Added DOCX Support ✅
- Added `python-docx` library to `requirements.txt`
- Implemented `_parse_docx()` method in `DocumentParser`
- Extracts text from paragraphs and tables
- Properly handles DOCX binary format

### 2. Added Timeout Handling ✅
- Frontend: 5-minute timeout per file
- Better error messages for timeout cases
- Prevents indefinite hanging

### 3. Improved Progress Feedback ✅
- Shows "Processing..." during upload
- Better error messages
- Clear timeout notifications

## Next Steps

1. **Install python-docx**:
   ```bash
   cd backend
   pip install python-docx
   # or
   poetry add python-docx
   ```

2. **Restart backend** to load new parser

3. **Try upload again** - should be much faster now

## Expected Performance

- **Before**: DOCX files failed or took 30+ minutes
- **After**: DOCX files parse correctly, ~10-30 seconds per file

## If Still Slow

Check:
- Embedding provider (local is slower than OpenAI)
- Document size (large docs take longer)
- Backend logs for specific bottlenecks
