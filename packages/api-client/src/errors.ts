export class ApiClientError extends Error {
  public statusCode: number;
  public details?: unknown;

  constructor(message: string, statusCode: number, details?: unknown) {
    super(message);
    this.name = 'ApiClientError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

export class NetworkError extends ApiClientError {
  constructor(message: string = 'Network connectivity error') {
    super(message, 0);
    this.name = 'NetworkError';
  }
}

export class UnauthorizedError extends ApiClientError {
  constructor(message: string = 'Authentication required') {
    super(message, 401);
    this.name = 'UnauthorizedError';
  }
}
