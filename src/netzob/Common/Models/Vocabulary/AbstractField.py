#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import uuid
import abc
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Common.Utils.UndoRedo.AbstractMementoCreator import AbstractMementoCreator
from netzob.Common.Utils.NetzobRegex import NetzobRegex
from netzob.Common.Models.Vocabulary.Functions.EncodingFunction import EncodingFunction
from netzob.Common.Models.Vocabulary.Functions.VisualizationFunction import VisualizationFunction
from netzob.Common.Models.Vocabulary.Functions.TransformationFunction import TransformationFunction
from netzob.Common.Utils.TypedList import TypedList


class InvalidVariableException(Exception):
    """This exception is raised when the variable behing the definition
    a field domain (and structure) is not valid. The variable definition
    is upgraded everytime the domain is modified.
    """
    pass


class AlignmentException(Exception):
    pass


class NoSymbolException(Exception):
    pass


class AbstractField(AbstractMementoCreator):
    """Represents all the different classes which participates in fields definitions of a message format."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, name=None, regex=None, layer=False):
        self.__logger = logging.getLogger(__name__)
        self.__id = uuid.uuid4()
        self.__name = name
        self.__regex = regex
        self.__layer = layer
        self.__description = ""

        self.__children = TypedList(AbstractField)
        self.__parent = None

        self.__encodingFunctions = TypedList(EncodingFunction)
        self.__visualizationFunctions = TypedList(VisualizationFunction)
        self.__transformationFunctions = TypedList(TransformationFunction)

        self._variable = None

    def getCells(self, encoded=False, styled=False, transposed=False):
        """Returns a matrix with a different line for each messages attached to the symbol of the current element.

        The matrix includes a different column for each leaf children of the current element.
        In each cell, the slices of messages once aligned.
        Attached :class:`EncodingFunction` can also be considered if parameter encoded is set to True.
        In addition, visualizationFunctions are also applied if parameter styled is set to True.
        If parameter Transposed is set to True, the matrix is built with rows for fields and columns for messages.

        :keyword encoded: if set to True, encoding functions are applied on returned cells
        :type encoded: :class:`bool`
        :keyword styled: if set to True, visualization functions are applied on returned cells
        :type styled: :class:`bool`
        :keyword transposed: is set to True, the returned matrix is transposed (1 line for each field)
        :type transposed: :class:`bool`

        :return: a matrix representing the aligned messages following fields definitions.
        :rtype: a :class:`list` of :class:`list` of :class:`str`
        :raises: :class:`netzob.Common.Models.Vocabulary.AbstractField.AlignmentException` if an error occurs while aligning messages
        """
        return [[]]

    def getValues(self, encoded=False, styled=False):
        """Returns all the values the current element can take following messages attached to the symbol of current element.

        Specific encodingFunctions can also be considered if parameter encoded is set to True.
        In addition, visualizationFunctions are also applied if parameter styled is set to True.

        :keyword encoded: if set to True, encoding functions are applied on returned cells
        :type encoded: :class:`bool`
        :keyword styled: if set to True, visualization functions are applied on returned cells
        :type styled: :class:`bool`

        :return: a list detailling all the values current element takes.
        :rtype: a :class:`list` of :class:`str`
        :raises: :class:`netzob.Common.Models.Vocabulary.AbstractField.AlignmentException` if an error occurs while aligning messages
        """
        return []

    @abc.abstractmethod
    def generate(self, mutator=None):
        """Generate a :class:`netzob.Common.Models.Vocabulary.Messages.RawMessage` which content
        follows the fields definitions attached to current element.

        :keyword mutator: if set, the mutator will be used to mutate the fields definitions
        :type mutator: :class:`netzob.Common.Models.Mutators.AbstractMutator`

        :return: a generated content represented with an hexastring
        :rtype: :class:`str`
        :raises: :class:`netzob.Common.Models.Vocabulary.AbstractField.GenerationException` if an error occurs while generating a message
        """
        return

    def getSymbol(self):
        """Computes the symbol to which this field is attached.

        To retrieve it, this method recursively call the parent of the current object until the root is found.
        If the last root is not a :class:`netzob.Common.Models.Vocabulary.Symbol`, it raises an Exception.

        :returns: the symbol if available
        :type: :class:`netzob.Common.Models.Vocabulary.Symbol`
        :raises: :class:`netzob.Common.Models.Vocabulary.AbstractField.NoSymbolException`
        """
        from netzob.Common.Models.Vocabulary.Symbol import Symbol
        if isinstance(self, Symbol):
            return self
        elif self.hasParent():
            return self.parent.getSymbol()
        else:
            raise NoSymbolException()

    def hasParent(self):
        """Computes if the current element has a parent.

        :returns: True if current element has a parent.
        :rtype: :class:`bool`
        """
        return self.__parent is not None

    def clearChildren(self):
        """Remove all the children attached to the current element"""

        while(len(self.__children) > 0):
            self.__children.pop()

    def clearEncodingFunctions(self):
        """Remove all the encoding functions attached to the current element"""

        while(len(self.__encodingFunctions) > 0):
            self.__encodingFunctions.pop()

    def clearVisualizationFunctions(self):
        """Remove all the visualization functions attached to the current element"""

        while(len(self.__visualizationFunctions) > 0):
            self.__visualizationFunctions.pop()

    def clearTransformationFunctions(self):
        """Remove all the transformation functions attached to the current element"""

        while(len(self.__transformationFunctions) > 0):
            self.__transformationFunctions.pop()

    # PROPERTIES

    @property
    def id(self):
        """Unique identifier of the field.

        This value must be a unique UUID instance (generated with uuid.uuid4()).

        :type: :class:`uuid.UUID`
        :raises: :class:`TypeError`, :class:`ValueError`
        """

        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, id):
        if id is None:
            raise ValueError("id is Mandatory.")
        self.__id = id

    @property
    def name(self):
        """Public name (may not be unique), default value is None

        :type: :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__name

    @name.setter
    @typeCheck(str)
    def name(self, name):
        self.__name = name

    @property
    def regex(self):
        """Represents the variable size of the field through the use a specific regex representation.

        :type: :class:`netzob.Common.Utils.NetzobRegex.NetzobRegex`
        :raises: :class:`TypeError`
        """

        return self.__regex

    @regex.setter
    @typeCheck(NetzobRegex)
    def regex(self, regex):
        self.__regex = regex

    @property
    def layer(self):
        """Flag describing if element is a layer.

        :type: :class:`bool`
        :raises: :class:`TypeError`
        """

        return self.__layer

    @layer.setter
    @typeCheck(bool)
    def layer(self, layer):
        if layer is None:
            layer = False
        self.__layer = layer

    @property
    def description(self):
        """User description of the field. Default value is ''.

        :type: :class:`str`
        :raises: :class:`TypeError`
        """

        return self.__description

    @description.setter
    @typeCheck(str)
    def description(self, description):
        self.__description = description

    @property
    def encodingFunctions(self):
        """Sorted typed list of encoding function to attach on field.

        .. note:: list implemented as a :class:`netzob.Common.Utils.TypedList.TypedList`

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Functions.EncodingFunction`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__encodingFunctions

    @encodingFunctions.setter
    def encodingFunctions(self, encodingFunctions):
        self.clearEncodingFunctions()
        self.encodingFunctions.extend(encodingFunctions)

    @property
    def visualizationFunctions(self):
        """Sorted list of visualization function to attach on field.

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Functions.VisualizationFunction`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__visualizationFunctions

    @visualizationFunctions.setter
    def visualizationFunctions(self, visualizationFunctions):
        self.clearVisualizationFunctions()
        self.visualizationFunctions.extend(visualizationFunctions)

    @property
    def transformationFunctions(self):
        """Sorted list of transformation function to attach on field.

        :type: a list of :class:`netzob.Common.Models.Vocabulary.Functions.TransformationFunction`
        :raises: :class:`TypeError`

        .. warning:: Setting this value with a list copies its members and not the list itself.
        """

        return self.__transformationFunctions

    @transformationFunctions.setter
    def transformationFunctions(self, transformationFunctions):
        self.clearTransformationFunctions()
        self.transformationFunctions.extend(transformationFunctions)

    @property
    def children(self):
        """Sorted list of field children."""

        return self.__children

    @children.setter
    def children(self, children):
        self.clearChildren()
        self.children.extend(children)

    @property
    def parent(self):
        """The parent of this current element.

        If current element has no parent, its value is **None**.

        :type: a :class:`netzob.Common.Models.Vocabulary.AbstractField.AbstractField`
        :raises: :class:`TypeError`
        """

        return self.__parent

    @parent.setter
    @typeCheck("SELF")
    def parent(self, parent):
        self.__parent = parent

    def storeInMemento(self):
        pass

    def restoreFromMemento(self, memento):
        pass