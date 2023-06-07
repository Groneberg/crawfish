import os
import config

from dotenv import load_dotenv
from pathlib import Path

from src import labelbox_annotations
from src import labelbox_video_json_transformer
from src import video_frame_thinning


def prepare_labelbox_dataset_for_yolo() -> int:
	dotenv_path = Path('../.env.local')
	load_dotenv(dotenv_path=dotenv_path)

	if not os.getenv('LABELBOX_API_KEY'):
		print('LABELBOX_API_KEY not set. Create a .env.local file in the root directory and set the key there.')
		return 1

	if not os.path.exists(config.DIR_CURRENT_DATASET):
		os.makedirs(config.DIR_CURRENT_DATASET)

	if not os.path.exists(config.LABELBOX_ANNOTATIONS_EXPORT_PATH):
		labelbox_annotations.download_json(os.getenv('LABELBOX_API_KEY'))

	if not os.path.exists(config.DIR_TRAINING):
		os.makedirs(config.DIR_TRAINING)

	labelbox_video_json_transformer.convert_to_yolo(
		input_json_path=config.LABELBOX_ANNOTATIONS_EXPORT_PATH,
		output_directory=config.DIR_TRAINING
	)

	# todo: download videos from labelbox

	# todo: extract frames from videos

	if not os.path.exists(config.DIR_DISCARD):
		os.makedirs(config.DIR_DISCARD)

	video_frame_thinning.keep_nth_frame(
		source_dir=config.DIR_TRAINING,
		discard_dir=config.DIR_DISCARD,
		keep_nth_frame=config.THINNING_KEEP_NTH_FRAME
	)

	# todo: validate annotations

	# todo: split dataset into train, test, (validation)

	# todo: augment dataset


if __name__ == '__main__':
	prepare_labelbox_dataset_for_yolo()
