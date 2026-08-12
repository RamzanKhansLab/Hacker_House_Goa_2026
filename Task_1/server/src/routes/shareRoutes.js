import { Router } from "express";
import { createShare, getSharePage } from "../controllers/shareController.js";

export const shareRouter = Router();

shareRouter.post("/api/share", createShare);
shareRouter.get("/share/:slug", getSharePage);
