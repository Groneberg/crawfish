import os
import shutil

import config

from dotenv import load_dotenv
from pathlib import Path

from src import labelbox_annotations, video_processing
from split_dataset import split_dataset
from augement_dataset import run_augmentations


def prepare_labelbox_dataset_for_yolo() -> int:
	print('Preparing labelbox dataset for YOLO...')
	dotenv_path = Path('../.env.local')
	load_dotenv(dotenv_path=dotenv_path)

	if not os.getenv('LABELBOX_API_KEY'):
		print('LABELBOX_API_KEY not set. Create a .env.local file in the root directory and set the key there.')
		return 1

	# Download labelbox annotations
	if not os.path.exists(config.DIR_CURRENT_DATASET):
		os.makedirs(config.DIR_CURRENT_DATASET)

	labelbox_annotations.download_project_json(
		os.getenv('LABELBOX_API_KEY'),
		config.LABELBOX_PROJECT_ID,
		config.LABELBOX_EXPORT_PARAMETERS
	)

	# Remove video annotations without project data, sice the labelbox API returns all videos
	labelbox_annotations.remove_invalid_videos_from_annotations(
		input_json_path=config.LABELBOX_ANNOTATIONS_EXPORT_PATH
	)

	# Thin out the number of frames in the project json. Reducing it here will reduce the work for all subsequent steps.
	labelbox_annotations.thin_out_frame_annotations(
		input_json_path=config.LABELBOX_ANNOTATIONS_EXPORT_PATH,
		keep_nth_frame=config.THINNING_KEEP_NTH_FRAME
	)

	# Convert labelbox annotations to YOLO format
	if not os.path.exists(config.DIR_TRAINING):
		os.makedirs(config.DIR_TRAINING)
	labelbox_annotations.convert_to_yolo(
		input_json_path=config.LABELBOX_ANNOTATIONS_EXPORT_PATH,
		output_directory=config.DIR_TRAINING
	)

	# Download videos
	if not os.path.exists(config.DIR_VIDEOS):
		os.makedirs(config.DIR_VIDEOS)
	video_processing.download_project_videos(
		input_json_path=config.LABELBOX_ANNOTATIONS_EXPORT_PATH,
		output_dir=config.DIR_VIDEOS
	)

	# extract and resize frames from videos
	video_processing.extract_and_resize_frames_from_videos()

	# Reduce the number of frames in the dataset by keeping only every nth frame
	if not os.path.exists(config.DIR_DISCARD):
		os.makedirs(config.DIR_DISCARD)

	# Redundant, since we're already thinning out the frames in the labelbox annotations
	# video_frame_thinning.keep_nth_frame(
	# 	source_dir=config.DIR_TRAINING,
	# 	discard_dir=config.DIR_DISCARD,
	# 	keep_nth_frame=config.THINNING_KEEP_NTH_FRAME
	# )

	# todo: validate annotations

	# split dataset into train, test, (validation)
	split_dataset(config.DIR_VIDEOS)

	# augment current yolo dataset to increase the number of training images
	if not os.path.exists(config.DIR_AUGMENTED):
		os.makedirs(config.DIR_AUGMENTED)

	if config.AUGMENTATION_ENABLED:
		run_augmentations(config.DIR_TRAINING, config.DIR_AUGMENTED)
		shutil.copytree(config.DIR_AUGMENTED, config.DIR_TRAINING)
		# TODO: remove augmented images from training set when done / not needed currently
		# TODO: add progress bar for augmentation


def train_yolo():
    pass


def predict_yolo():
    pass


if __name__ == '__main__':
    prepare_labelbox_dataset_for_yolo()
