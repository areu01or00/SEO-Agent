export class BaseModule {
    dataForSEOClient;
    constructor(dataForSEOClient) {
        this.dataForSEOClient = dataForSEOClient;
    }
    formatError(error) {
        return error instanceof Error ? error.message : 'Unknown error';
    }
    formatResponse(data) {
        return {
            content: [
                {
                    type: "text",
                    text: JSON.stringify(data, null, 2),
                },
            ],
        };
    }
    formatErrorResponse(error) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${this.formatError(error)}`,
                },
            ],
        };
    }
}
