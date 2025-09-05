# Search Engine Implementation for Step 3

## Overview

This document describes the complete implementation of the search engine for step 3 of the audience creation process. The search engine allows users to search across multiple social platforms including GoFundMe.com, X.com, Reddit.com, and other platforms using generated keywords and phrases.

## Features

- **Real-time Search**: Start, pause, stop, and resume search operations
- **Multi-platform Support**: Currently implements GoFundMe.com scraping, with placeholders for X and Reddit
- **Progress Tracking**: Real-time progress updates with platform-specific status
- **Database Persistence**: All search results are saved to MongoDB for later retrieval
- **State Persistence**: Search state is maintained across page refreshes (F5)
- **Modern UI**: Clean, responsive interface with search controls and results display

## Architecture

### 1. Search Engine (`utils/search_engine.py`)

The core search engine class that handles:
- Platform-specific scraping logic
- Search state management
- Progress tracking
- Error handling

```python
from utils.search_engine import search_engine

# Start a search
results = search_engine.start_search(keywords, phrases, user_id, audience_id)

# Get current status
status = search_engine.get_search_status()

# Control search operations
search_engine.pause_search()
search_engine.resume_search()
search_engine.stop_search()
```

### 2. Search Results Model (`models/search_results.py`)

Database model for storing and retrieving search results:

```python
from models.search_results import save_search_results, get_search_results_by_audience

# Save results
save_search_results(user_id, audience_id, results)

# Retrieve results
results = get_search_results_by_audience(audience_id, user_id)
```

### 3. Updated Routes (`routes/audiences.py`)

Enhanced step 3 route with multiple actions:

- `POST /audiences/create/step3` - Handle search actions
- `GET /audiences/search/status/<audience_id>` - Get search status
- `POST /audiences/search/start` - Start background search

### 4. Enhanced Template (`templates/create_audience.html`)

Modern UI with:
- Search controls (Start, Pause, Stop, Resume)
- Real-time progress bar
- Platform-specific status updates
- Results table with filtering
- Responsive design

## Usage

### Starting a Search

1. Navigate to step 3 of audience creation
2. Review your keywords and phrases
3. Click "Start Search" button
4. Monitor progress in real-time
5. Use pause/stop controls as needed

### Search Controls

- **Start Search**: Initiates the search process across all platforms
- **Pause**: Temporarily halts the search (can be resumed)
- **Stop**: Completely stops the search process
- **Resume**: Continues a paused search

### Progress Tracking

The search engine provides real-time updates:
- Current platform being searched
- Progress percentage
- Results count
- Error status

### Results Display

Search results are displayed in a table showing:
- Platform source
- Campaign/post title
- Creator/author
- Location
- Date
- Relevance score

## Database Schema

### Search Results Collection

```javascript
{
  "_id": ObjectId,
  "platform": "GoFundMe",
  "name": "Campaign Title",
  "creator": "Creator Name",
  "location": "City, State",
  "date": "2024-01-01",
  "description": "Campaign description",
  "url": "https://gofundme.com/f/...",
  "relevance_score": 8,
  "keywords_matched": ["keyword1", "keyword2"],
  "user_id": "user_id",
  "audience_id": "audience_id",
  "created_at": ISODate,
  "status": "active"
}
```

## Platform Implementation

### GoFundMe.com

**Status**: ✅ Fully Implemented

- Uses Selenium WebDriver for dynamic content
- Extracts campaign information:
  - Title
  - Creator
  - Location
  - Date
  - Description
  - URL
- Implements rate limiting and error handling
- Scrolls pages to load more content

### X.com (Twitter)

**Status**: 🔄 Placeholder (Requires API Access)

- Currently returns empty results
- Future implementation will require Twitter API credentials
- Will search for relevant tweets and conversations

### Reddit.com

**Status**: 🔄 Placeholder (Requires API Access)

- Currently returns empty results
- Future implementation will require Reddit API credentials
- Will search subreddits for relevant discussions

### Other Platforms

**Status**: 🔄 Placeholder

- Framework ready for additional platform implementations
- Can easily add new scrapers following the same pattern

## Error Handling

The search engine includes comprehensive error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **Platform Changes**: Graceful degradation when selectors change
- **Rate Limiting**: Built-in delays between requests
- **Browser Crashes**: Automatic driver restart
- **Data Validation**: Ensures all required fields are present

## Performance Considerations

- **Concurrent Processing**: Each platform is processed sequentially to avoid overwhelming servers
- **Rate Limiting**: Built-in delays between requests to respect platform policies
- **Memory Management**: Results are processed in batches to avoid memory issues
- **Timeout Handling**: Automatic cleanup of long-running operations

## Security Features

- **User Isolation**: Users can only access their own search results
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Prevents abuse of the search functionality
- **Session Management**: Secure session handling with Flask-Login

## Installation Requirements

Add these dependencies to `requirements.txt`:

```
selenium==4.15.2
beautifulsoup4==4.12.2
webdriver-manager==4.0.1
lxml==4.9.3
```

## Testing

Run the test script to verify functionality:

```bash
python test_search.py
```

## Future Enhancements

1. **Background Processing**: Implement Celery for true background search processing
2. **More Platforms**: Add support for LinkedIn, Facebook Groups, Discord
3. **Advanced Filtering**: Implement ML-based relevance scoring
4. **Export Options**: Add CSV, Excel, and API export capabilities
5. **Search History**: Track and analyze search performance over time

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   - Ensure Chrome browser is installed
   - Check webdriver-manager is working correctly

2. **Rate Limiting**
   - Increase delays between requests
   - Use proxy rotation for high-volume searches

3. **Memory Issues**
   - Reduce batch sizes
   - Implement result streaming

4. **Platform Changes**
   - Update CSS selectors in the search engine
   - Test with sample URLs

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export SEARCH_DEBUG=1
```

## Support

For issues or questions about the search engine:

1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test with the provided test script
4. Review the database connection settings

## Conclusion

The search engine provides a robust, scalable solution for searching social platforms. It's designed to be easily extensible for new platforms while maintaining good performance and user experience. The implementation follows best practices for web scraping, error handling, and user interface design.
