from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from typing import Optional, List, Any

# models for input
class FormSampleContainer(BaseModel):
    id: Optional[int] = Field(default=None)
    barcode: str = Field(min_length=8)
    reagent: Optional[str] = Field(default=None)
    lot: str
    lot_id: Optional[int] = Field(default=None)
    amount: int = Field(gt=0, description="The amount of sample in the container")
    unit: Optional[str] = Field(description="The unit of measure for amount", default="uL")
    concentration: int = Field(gt=0, description="The concentration of sample in the container")
    concentration_unit: Optional[str] = Field(description="The unit of measure for concentration", default="uM")
    container_type:str = Field(description="The type of the container", default="vial")


class FormLocateContainer(BaseModel):
    barcode: str = Field(min_length=8)
    parent_barcode: str = Field(min_length=8)
    position: str = Field(min_length=1)


# this represents one line of the pick list request.  we expect to get a list of them for one request
class FormPickListItem(BaseModel):
    reagent: str
    amount: int = Field(gt=0)
    concentration: int = Field(gt=0)

########################################################################################################################

# models for output, better than dicts???
# not dealing with it right now

# problem - some children can be empty locations, so sticking with dictionaries for now
# two separate models for containers because we want to minimize the null values returned, especially for the child containers
# a container which holds other containers.  never a sample
class RetParentContainer(BaseModel):
    id: int
    barcode: str
    container_type: str
    position: Optional[str] = Field(default=None)
    # Any type because they can be other parent containers or sample containers
    child_containers: Optional[List[Any]] = Field(default=[])
# a container which holds a sample.  never has children
class RetSampleContainer(BaseModel):
    id: int
    barcode: str
    container_type: str
    position: Optional[str] = Field(default=None)
    reagent: str
    amount: int
    unit: str
    concentration: int
    concentration_unit: str







