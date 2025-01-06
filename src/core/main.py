import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image

from src.common.validate import validate_config
from src.utils.calc import calculate_possible_combinations
from src.utils.io import read_json, write_file, write_json
from src.utils.logger import get_logger, get_progress_bar
from src.utils.random import seeded_weighted_selection


class Generator:
    def __init__(self, **args):
        # Set verbosity level and initialize logger
        self.logger = get_logger(args["verbose"])

        if args["command"] in ["generate", "validate"]:
            if not args["config"]:
                raise ValueError("No configuration file was provided.")
            elif not args["config"].endswith(".json"):
                raise ValueError(f"Invalid configuration file '{args['config']}'")

            if not args["amount"]:
                raise ValueError("No amount was provided.")
            elif not isinstance(args["amount"], int) or args["amount"] <= 0:
                raise ValueError(f"Invalid amount '{args['amount']}'")
            self.amount = args["amount"]
            self.no_pad = args["no_pad"]
            self.pad_amount = 0 if self.no_pad else len(str(self.amount))

            # Read configuration and validate it
            self.logger.debug(f"Loading configuration from '{args['config']}'")
            self.config = read_json(args["config"])
            self.logger.debug("Validating configuration")
            validate_config(self.config)

        # Set arguments
        self.seed = (
            int(args["seed"])
            if args["seed"] is not None
            else int.from_bytes(random.randbytes(16), byteorder="little")
        )
        self.start_at = int(args["start_at"])
        self.output = args["output"]
        self.allow_duplicates = args["allow_duplicates"]
        self.image_path = args["image_path"]

        # Initialize state
        self.nonce = 0
        self.all_genomes = []

    def _tomlify(self) -> str:
        """
        Converts a dictionary to TOML format.
        """
        toml = ""
        obj = {
            "amount": self.amount,
            "seed": self.seed,
            "start_at": self.start_at,
            "output": self.output,
            "allow_duplicates": self.allow_duplicates,
            "no_pad": self.no_pad,
        }
        for key, value in obj.items():
            toml += f"{key} = {value}\n"
        return toml

    def __build_genome_metadata(self, token_id: int = 0):
        """
        Builds the generation / NFT metadata for a single NFT.
        """
        genome_traits = {}

        # Select traits for each layer
        for layer in self.config["layers"]:
            trait_values_and_weights = list(zip(layer["values"], layer["weights"]))
            genome_traits[layer["name"]] = seeded_weighted_selection(
                trait_values_and_weights, seed=self.seed, nonce=self.nonce
            )
            self.nonce += 1

        # Check for incompatibilities
        for incompatibility in self.config["incompatibilities"]:
            for trait in genome_traits:
                if (
                    genome_traits[incompatibility["layer"]] == incompatibility["value"]
                    and genome_traits[trait] in incompatibility["incompatible_with"]
                ):
                    if "default" in incompatibility:
                        genome_traits[trait] = incompatibility["default"]["value"]
                    else:
                        return self.__build_genome_metadata(token_id)

        if genome_traits in self.all_genomes and not self.allow_duplicates:
            return self.__build_genome_metadata(token_id)
        else:
            metadata = {
                "token_id": token_id,
                "image": f"{self.output}/images/{token_id}.png",
                "name": f"{self.config['name']}{str(token_id).zfill(self.pad_amount)}",
                "description": self.config["description"],
                "attributes": [
                    {"trait_type": layer["name"], "value": genome_traits[layer["name"]]}
                    for layer in self.config["layers"]
                ],
            }
            self.all_genomes.append(metadata)
            return metadata

    def __build_genome_image(self, metadata: dict):
        """
        Builds the NFT image for a single NFT.
        """
        self.logger.info(f"Generating image for token_id: {metadata['token_id']}")
        layers = []
        for index, attr in enumerate(metadata["attributes"]):
            # Get the image for the trait
            trait_name = attr["trait_type"]
            trait_value = attr["value"]
            for i, trait in enumerate(self.config["layers"][index]["values"]):
                if trait == trait_value:
                    img_path = os.path.join(
                        self.config["layers"][index]["trait_path"],
                        f"{self.config['layers'][index]['filename'][i]}.png",
                    )
                    self.logger.debug(f"Attempting to load layer '{trait_name}': {img_path}")
                    if os.path.exists(img_path):
                        try:
                            layers.append(Image.open(img_path).convert("RGBA"))
                            self.logger.debug(f"Successfully loaded layer '{trait_name}': {img_path}")
                        except Exception as e:
                            self.logger.error(f"Error loading image '{img_path}' for '{trait_name}': {e}")
                    else:
                        self.logger.error(f"Missing image file: {img_path} for '{trait_name}'")
                    break

        if not layers:
            self.logger.error(f"No valid layers found for token_id: {metadata['token_id']}")
            return

        try:
            # Composite layers
            main_composite = layers[0]
            for layer in layers[1:]:
                main_composite = Image.alpha_composite(main_composite, layer)

            # Ensure the images directory exists
            os.makedirs(f"{self.output}/images", exist_ok=True)

            # Save the final composite image
            output_path = f"{self.output}/images/{metadata['token_id']}.png"
            main_composite.save(output_path)
            self.logger.info(f"Saved image to: {output_path}")
        except Exception as e:
            self.logger.error(
                f"Failed to generate image for token_id {metadata['token_id']}: {e}"
            )

        if not layers:
            self.logger.error(f"No valid layers found for token_id: {metadata['token_id']}")
            return

        try:
            # Composite layers
            main_composite = layers[0]
            for layer in layers[1:]:
                main_composite = Image.alpha_composite(main_composite, layer)

            # Ensure the images directory exists
            os.makedirs(f"{self.output}/images", exist_ok=True)

            # Save the final composite image
            output_path = f"{self.output}/images/{metadata['token_id']}.png"
            main_composite.save(output_path)
            self.logger.info(f"Saved image to: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to generate image for token_id {metadata['token_id']}: {e}")

    def generate(self):
        """
        Generates the NFTs with the given configuration.
        """
        self.logger.info("Starting generation")

        max_combinations = calculate_possible_combinations(self.config)
        self.logger.debug(
            f"There are {max_combinations:,} possible unique combinations of this configuration"
        )
        if self.amount > max_combinations and not self.allow_duplicates:
            raise ValueError(
                f"Amount of NFTs to generate ({self.amount:,}) exceeds the number of possible unique combinations ({max_combinations:,})"
            )

        self.logger.info(f"Generating metadata for {self.amount} NFTs")
        os.makedirs(f"{self.output}/metadata", exist_ok=True)

        for i in range(self.amount):
            token_id = self.start_at + i
            metadata = self.__build_genome_metadata(token_id)
            write_json(f"{self.output}/metadata/{token_id}.json", metadata)

        write_json(f"{self.output}/metadata/all-objects.json", self.all_genomes)
        write_file(f"{self.output}/.generatorrc", self._tomlify())

        self.logger.info(f"Generating layered images for {self.amount} NFTs")
        os.makedirs(f"{self.output}/images", exist_ok=True)

        with ThreadPoolExecutor(max_workers=25) as pool:
            futures = [
                pool.submit(self.__build_genome_image, genome)
                for genome in self.all_genomes
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Image generation error: {e}")

        self.logger.info("Generation complete!")
