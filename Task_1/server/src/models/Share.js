import mongoose from "mongoose";

const shareSchema = new mongoose.Schema({
  slug: { type: String, required: true, unique: true, index: true },
  imageFileName: { type: String, required: true },
  format: { type: String, enum: ["pfp", "id-card"], required: true },
  createdAt: { type: Date, default: Date.now, required: true },
  expiresAt: { type: Date, required: true, expires: 0 },
}, { versionKey: false });

export const Share = mongoose.models.Share || mongoose.model("Share", shareSchema);
