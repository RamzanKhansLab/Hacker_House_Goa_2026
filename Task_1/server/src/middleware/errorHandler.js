export function notFoundHandler(request, response) {
  response.status(404).json({ message: "Route not found." });
}

export function errorHandler(error, request, response, next) { // eslint-disable-line no-unused-vars
  console.error(error);
  if (error?.type === "entity.too.large" || error?.status === 413) {
    return response.status(413).json({ message: "This generated image is too large to share. Download it and share manually." });
  }
  return response.status(500).json({ message: "We couldn't prepare a share link. Your graphic is still ready to download." });
}
